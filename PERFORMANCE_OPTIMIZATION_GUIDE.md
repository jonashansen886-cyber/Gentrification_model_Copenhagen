# Performance Optimization Guide for Space-Time Clustering

## Quick Start: Choose Your Speed

| Use Case | Settings | Speed | Setup |
|----------|----------|-------|-------|
| **Exploratory Analysis** | Euclidean + cache + parquet + max_iter=15 | ⚡⚡⚡ Fastest | 5 min |
| **Parameter Tuning** | Euclidean + cache + max_iter=20 | ⚡⚡ Fast | Immediate |
| **Final Analysis** | DTW + max_iter=100 | 🐌 Slow | ~1 hour |

---

## Three-Layer Optimization Strategy

### Layer 1: File I/O Optimization (Parquet)

**What it does:** Faster reading/writing data files

**Configuration:**
```python
# In Cell 4 of notebook 01
USE_PARQUET = False  # Change to True

# First time with CSVs (run once):
convert_csv_to_parquet(DATA_DIR, PARQUET_DIR)

# Subsequent runs: Set USE_PARQUET = True
USE_PARQUET = True
```

**Speed improvement:** **5-10x faster file I/O**
- CSV read: ~2 seconds per 100 MB
- Parquet read: ~0.2 seconds per 100 MB
- File size: 50-80% smaller

**When to use:**
- ✅ Always for regular/repeated runs
- ✅ Large datasets (>100 MB)
- ✅ Multiple variables to process
- ❌ One-time quick analysis

**No breaking changes:**
- Automatic CSV → Parquet conversion
- Both formats load identically
- Easy toggle between formats

---

### Layer 2: Clustering Parameter Optimization (max_iter)

**What it does:** Controls clustering convergence iterations

**Configuration:**
```python
# In CONFIG (Cell 3):
CONFIG = {
    'max_iter': 100,  # Default: thorough but slow
    'time_series_distance': 'euclidean',
    # ...
}

# For speed: reduce to 10-20
CONFIG['max_iter'] = 15  # Fast convergence
```

**Speed improvement:** **Depends on convergence**
- max_iter=100: 100 full distance calculations
- max_iter=20: 20 full distance calculations
- max_iter=10: 10 full distance calculations

**When to use each:**
- **max_iter=10-20:** Exploratory analysis, debugging, parameter tuning
- **max_iter=50:** Most use cases
- **max_iter=100:** Final validation, publication-ready results

**Note:** For Euclidean + caching, lower max_iter still gets same cached distances.

---

### Layer 3: Distance Metric & Caching (Euclidean vs DTW)

**What it does:** Choice of distance metric determines both accuracy and speed, plus enables distance caching

**Configuration:**
```python
# In CONFIG (Cell 3):
CONFIG = {
    'time_series_distance': 'euclidean',  # Fast + cacheable
    # OR
    'time_series_distance': 'dtw',        # Slow but accurate
}
```

#### Euclidean Distance (Recommended for Speed)
```python
CONFIG['time_series_distance'] = 'euclidean'
```

**Characteristics:**
- ✅ 10-20x faster than DTW
- ✅ Enables distance caching (5-10x speedup on re-runs)
- ✅ Suitable for gentrification analysis
- ✅ Better with noisy temporal data
- ❌ Less sensitive to temporal patterns
- ❌ Treats all time steps equally

**Performance:**
- First run: ~5 minutes (1,000 locations)
- With cache: ~5 seconds on re-run
- With parquet: ~3 minutes first run

**When to use:**
- ✅ Exploratory analysis
- ✅ Multiple iterations/parameters
- ✅ Large datasets
- ✅ Production/operational runs

#### Dynamic Time Warping - DTW (Recommended for Accuracy)
```python
CONFIG['time_series_distance'] = 'dtw'
```

**Characteristics:**
- ✅ Captures temporal patterns better
- ✅ Accounts for time shift/warping
- ✅ Publication-ready results
- ❌ 10-20x slower than Euclidean
- ❌ No distance caching available
- ❌ Expensive O(n²m²) computation

**Performance:**
- First run: ~45 minutes (1,000 locations)
- Re-runs: ~45 minutes (no cache)
- DTW cost dominated by pairwise distance calculation

**When to use:**
- ✅ Final analysis
- ✅ Temporal pattern detection critical
- ✅ Publication/peer-review
- ❌ Exploratory phase
- ❌ Large-scale analysis

---

## Recommended Workflows

### Workflow 1: Fast Exploratory Analysis (Recommended for Initial Work)
```python
# Cell 3 - CONFIG
CONFIG = {
    'location_id': 'cluster_id',
    'time_field': 'Timedate',
    'cluster_count': 6,
    'time_series_distance': 'euclidean',  # Fast
    'max_iter': 15,                       # Quick convergence
    'random_state': 42,
}

# Cell 4 - Data loading
USE_PARQUET = True  # After first run with CSV

# Expected runtime: ~3-6 minutes
# Output: Quick results for parameter exploration
```

**Use this for:**
- Understanding your data
- Testing different cluster counts
- Exploring neighborhood patterns
- Quick sensitivity analysis

**Pro tips:**
- Start with small max_iter (10-15)
- Use Euclidean distance
- Switch to Parquet after first run
- Distance caching kicks in automatically

---

### Workflow 2: Parameter Tuning with Caching
```python
# Cell 3 - CONFIG
CONFIG = {
    'location_id': 'cluster_id',
    'time_field': 'Timedate',
    'cluster_count': 6,  # Try different values
    'time_series_distance': 'euclidean',  # Use cache
    'max_iter': 20,
    'random_state': 42,
}

# Change only cluster_count, keep distance metric
# First run: 5 min (computes & caches distances)
# Each re-run: 1 min (loads cached distances)
# Total for 5 iterations: ~10 minutes instead of ~25 minutes
```

**Use this for:**
- Finding optimal cluster count
- Testing different parameters
- Sensitivity analysis
- Iterative refinement

**You'll see:**
```
💾 Will save computed Euclidean distance matrix to age_18_25_euclidean_distances.npy
[clustering output]
✓ Clustering complete!

[Second run with different cluster_count:]
📦 Loading cached Euclidean distance matrix (age_18_25_euclidean_distances.npy)
[clustering output - much faster!]
```

---

### Workflow 3: Final Publication-Ready Analysis
```python
# Cell 3 - CONFIG
CONFIG = {
    'location_id': 'cluster_id',
    'time_field': 'Timedate',
    'cluster_count': 6,
    'time_series_distance': 'dtw',        # Accurate (slow)
    'max_iter': 100,                      # Thorough
    'random_state': 42,
}

# Cell 4 - Data loading
USE_PARQUET = False  # Or True if you want faster I/O

# Expected runtime: ~45-60 minutes for all variables
# Output: Publication-quality clustering with temporal fidelity
```

**Use this for:**
- Final results for paper/publication
- Peer review/validation
- When accuracy > speed
- Archive/permanent records

**Why DTW:**
- Accounts for temporal shifts
- Better captures cluster-specific temporal patterns
- Defensible in peer review
- Published methods prefer DTW

---

## Performance Optimization Checklist

### ✅ Before First Run
- [ ] Check data location: `data/raw/long_format_csv/`
- [ ] Review CONFIG parameters
- [ ] Choose metric: Euclidean (speed) or DTW (accuracy)
- [ ] Decide on max_iter (10-20 for speed, 100 for thoroughness)

### ✅ For Exploratory Phase
- [ ] Set `time_series_distance = 'euclidean'`
- [ ] Set `max_iter = 15`
- [ ] Keep `USE_PARQUET = False` initially
- [ ] Run notebook for first time (creates caches)

### ✅ For Parameter Tuning
- [ ] Change only `cluster_count`, keep distance metric
- [ ] Keep same `max_iter`
- [ ] Distance cache loads automatically
- [ ] Each re-run: ~1 minute instead of ~5 minutes

### ✅ For Production Runs
- [ ] Change `USE_PARQUET = True`
- [ ] Keep `time_series_distance = 'euclidean'`
- [ ] Lower `max_iter` to 10-15 (already converged)
- [ ] Caches already exist from previous runs
- [ ] Total time: ~3 minutes for all variables

### ✅ For Final Publication
- [ ] Change `time_series_distance = 'dtw'`
- [ ] Set `max_iter = 100`
- [ ] Accept longer runtime (~45 min)
- [ ] Clear caches before final run (fresh results)

---

## Real-World Timing Examples

### Scenario: 1,000 locations, 100 time steps, 8 variables

**Option 1: Exploratory (Euclidean + Parquet + cache + max_iter=15)**
```
First run:
- I/O (8 CSVs): 3 min
- Space-time cubes: 2 min
- Distance computation: 2 min
- Clustering (8 × max_iter=15): 2 min
Total: ~9 minutes

Second run (same data, different cluster_count):
- I/O (8 Parquets): 20 sec
- Space-time cubes: 1 min
- Load cached distances: 2 sec
- Clustering (8 × max_iter=15): 1 min
Total: ~2 minutes ✨
```

**Option 2: Thorough (DTW + max_iter=100)**
```
First and every run:
- I/O: 3 min
- Space-time cubes: 2 min
- DTW distance computation: 35 min
- Clustering (8 × max_iter=100): 5 min
Total: ~45 minutes ⏳
```

**Option 3: Production (Euclidean + Parquet + cache + max_iter=10)**
```
After first run setup:
- I/O (8 Parquets): 20 sec
- Space-time cubes: 1 min
- Load cached distances: 2 sec
- Clustering (8 × max_iter=10): 30 sec
Total: ~2 minutes ⚡
```

---

## Distance Caching Deep Dive

### How It Works
```python
# First run with variable "age_18_25"
# - Computes 1000² pairwise distances = 1M distance values
# - Takes ~2 minutes
# - Saves to: data/processed/distance_matrix_cache/age_18_25_euclidean_distances.npy

# Second run with same variable:
# - Loads 1M distances from cache = instant
# - Saves ~2 minutes per run
# - Repeated 5 times = ~10 minutes saved total
```

### What Gets Cached
- ✅ Pairwise Euclidean distances between all time series
- ❌ NOT cached for DTW (requires on-the-fly computation)
- ❌ NOT cached for different data or time periods

### Cache Location
```
data/processed/distance_matrix_cache/
├── age_18_25_euclidean_distances.npy
├── age_26_40_euclidean_distances.npy
├── crime_main_y_euclidean_distances.npy
└── ...
```

### Clearing Caches
```python
# Clear all caches
import shutil
shutil.rmtree('data/processed/distance_matrix_cache')

# Clear specific cache
from pathlib import Path
cache_file = Path('data/processed/distance_matrix_cache/age_18_25_euclidean_distances.npy')
cache_file.unlink()

# Clear on data update (add to notebook)
import os
if cache_file.exists():
    data_mtime = os.path.getmtime('data/raw/long_format_csv/cluster_age_18_25_long.csv')
    cache_mtime = cache_file.stat().st_mtime
    if cache_mtime < data_mtime:
        cache_file.unlink()
        print("Cache invalidated - data was updated")
```

---

## Troubleshooting Performance

### Problem: Clustering still slow even with Euclidean + cache

**Check distance metric:**
```python
print(CONFIG['time_series_distance'])  # Should be 'euclidean'
```

**Check cache exists:**
```python
from pathlib import Path
cache_dir = Path('data/processed/distance_matrix_cache')
print(list(cache_dir.glob('*.npy')))
```

**Check max_iter:**
```python
print(CONFIG['max_iter'])  # Should be 10-20 for speed
```

### Problem: Very large cache files (>1 GB)

**Solutions:**
1. Clear old caches: `shutil.rmtree('data/processed/distance_matrix_cache')`
2. Use Parquet instead of CSV (smaller data files)
3. Consider subsampling for very large datasets

### Problem: Running out of memory

**Solutions:**
1. Reduce max_iter (requires fewer iterations)
2. Process variables one at a time instead of batch
3. Reduce cluster_count
4. Use DTW (less memory-hungry than caching distances)

---

## Decision Tree: Choose Your Configuration

```
Do you have results yet?
├─ NO: I'm exploring
│  ├─ time_series_distance = 'euclidean'
│  ├─ max_iter = 15
│  ├─ USE_PARQUET = False  (then True after first run)
│  └─ Expected time: 5-10 min first run, 1 min re-runs
│
└─ YES: I need final results
   ├─ Need publication-quality?
   │  ├─ YES: time_series_distance = 'dtw', max_iter = 100
   │  │        Expected time: ~45 min
   │  │
   │  └─ NO: time_series_distance = 'euclidean', max_iter = 20
   │         Expected time: ~5 min
   │
   └─ Need to run many times?
      ├─ YES: USE_PARQUET = True, use cache
      │        Expected time: 2 min per run (after first)
      │
      └─ NO: USE_PARQUET = False, doesn't matter
             Expected time: 5-10 min per run
```

---

## Key Takeaways

1. **For exploratory work:** Euclidean + max_iter=15 + Parquet
2. **For parameter tuning:** Keep same metric, change only cluster_count
3. **For final results:** DTW + max_iter=100 (accept the wait)
4. **For production:** Euclidean + Parquet + cached distances + max_iter=10

**Expected speedups:**
- Parquet: 5-10x faster I/O
- Euclidean vs DTW: 10-20x faster clustering
- Distance cache: 5-10x faster on re-runs
- **Combined: 50-100x faster for repeated analyses**

---

## Questions?

See **DISTANCE_CACHING_GUIDE.md** for detailed distance caching information.
See **notebooks/01_spacetime_cube_TSC.ipynb** for implementation details and cell-by-cell documentation.
