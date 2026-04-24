
import os
import re
import base64
import numpy as np

# Configuration
html_dir = 'results/metrics/charts_html'
output_file = 'results/reports/reclassified.txt'

# Variables and their gentrification direction
# 1: Higher value/Increasing trend = More Gentrified (Value 1)
# -1: Lower value/Decreasing trend = More Gentrified (Value 1)
var_directions = {
    'age_18_25': -1,      # Displacement of young/student populations
    'age_26_40': 1,       # Target demographic for gentrifiers (young professionals)
    'age_41_55': 1,       # Mature gentrifiers / established professionals
    'age_56_69': -1,      # Displacement of older long-term residents
    'crime_main_y': -1,    # Decrease in crime is a hallmark of gentrification
    'disp_inc': 1,        # Primary indicator: Increase in disposable income
    'emp': 1,             # Influx of workforce-active residents
    'EMUB': 1,            # Singles (Enlig Mand Uden Børn) often lead gentrification
    'grund': -1,          # Decrease in low education (primary school only) indicates displacement
    'gym_erhv': -1,       # Decrease in vocational education levels relative to academic
    'lvu': 1,             # High education (Lang Videregående Uddannelse) is a key gentrifier trait
    'mean_price': 1,      # Rising property prices/rents
    'mean_sqm': 1,        # Increase in property value per square meter
    'mig_in': 1,          # High influx of new residents
    'mig_net': 1,         # Positive migration balance during growth phases
    'mig_out': -1,        # Stability vs Displacement (higher rank for lower/stable outflow)
    'ool': -1,            # Decrease in population outside the labor market
    'PMB': -1,            # Traditional families (Par Med Børn) often displaced by singles/couples initially
    'PUB': 1,             # Couples without children (Par Uden Børn) are typical gentrifiers
    'public_housing': -1, # Reduction in social housing stock/share
    'unemp': -1           # Decrease in unemployment rates
}

def extract_clusters(html_path):
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract cluster ID and base64 encoded y-data from Plotly JSON
        matches = re.findall(r'\"name\":\"Cluster ([0-9]+)\".*?\"y\":{\"dtype\":\"f8\",\"bdata\":\"(.*?)\"}', content)
        clusters = []
        for cid, bdata in matches:
            b64 = bdata.replace('\\u002f', '/')
            data = np.frombuffer(base64.b64decode(b64), dtype='float64')
            if len(data) > 0:
                clusters.append({
                    'id': int(cid),
                    'mean': np.mean(data),
                    'slope': data[-1] - data[0],
                    'data': data
                })
        return clusters
    except Exception as e:
        print(f"Error processing {html_path}: {e}")
        return []

def main():
    if not os.path.exists(html_dir):
        print(f"Directory {html_dir} not found.")
        return

    files = sorted([f for f in os.listdir(html_dir) if f.endswith('.html') and 'counts' not in f and 'qol' not in f])
    output_lines = []

    for filename in files:
        # Resolve variable base name from filename
        parts = filename.split('_')
        year_idx = -1
        for i, p in enumerate(parts):
            if re.match(r'^[0-9]{4}$', p):
                year_idx = i
                break
        
        if year_idx != -1:
            var_base = '_'.join(parts[:year_idx])
        else:
            var_base = filename.replace('_tsc_timeseries.html', '')
        
        lookup_var = None
        for k in var_directions.keys():
            if k in var_base or var_base in k:
                lookup_var = k
                break
        
        direction = var_directions.get(lookup_var, 1)
        clusters = extract_clusters(os.path.join(html_dir, filename))
        
        if not clusters:
            continue
        
        # Calculate Gentrification Index
        all_means = [c['mean'] for c in clusters]
        all_slopes = [c['slope'] for c in clusters]
        
        mean_min, mean_max = min(all_means), max(all_means)
        slope_min, slope_max = min(all_slopes), max(all_slopes)
        
        for c in clusters:
            # Normalize and apply direction
            nm = (c['mean'] - mean_min) / (mean_max - mean_min) if mean_max != mean_min else 0.5
            ns = (c['slope'] - slope_min) / (slope_max - slope_min) if slope_max != slope_min else 0.5
            c['gent_index'] = (nm * 0.5 * direction) + (ns * 0.5 * direction)
        
        # Rank: Highest gent_index = Rank 1 (Most Gentrified)
        clusters.sort(key=lambda x: x['gent_index'], reverse=True)
        
        mapping = {}
        num_c = len(clusters)
        for i, c in enumerate(clusters):
            if num_c > 1:
                val = int(round(1 + (i / (num_c - 1)) * 5))
            else:
                val = 3
            mapping[c['id']] = val
        
        cluster_str = ', '.join([f'cluster {cid+1} == {mapping[cid]}' for cid in sorted(mapping.keys())])
        output_lines.append(f'{filename}, {cluster_str}')

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    print(f'Successfully reclassified {len(output_lines)} charts.')

if __name__ == "__main__":
    main()
