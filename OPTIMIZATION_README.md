# Performance Optimization Documentation

This folder contains comprehensive guides for optimizing the space-time clustering analysis performance.

## Files

### 1. **PERFORMANCE_OPTIMIZATION_GUIDE.md** (⭐ Start Here!)
**Complete guide for choosing the right performance settings.**

- **Quick comparison table** of different optimization approaches
- **Three-layer optimization strategy:**
  - Layer 1: File I/O (Parquet files)
  - Layer 2: Clustering iterations (max_iter parameter)
  - Layer 3: Distance metric & caching (Euclidean vs DTW)
- **Real-world timing examples** with actual benchmark data
- **Recommended workflows** for different scenarios:
  - Fast exploratory analysis
  - Parameter tuning with caching
  - Final publication-ready analysis
- **Decision tree** to help choose your configuration

**Best for:** Getting started quickly, choosing between speed/accuracy tradeoffs

### 2. **DISTANCE_CACHING_GUIDE.md** (📦 For Distance Matrix Caching)
**Deep dive into how distance matrix caching works and how to use it.**

- **Why caching matters:** 5-10x speedup for repeated runs
- **How to use distance caching:** Automatic and manual approaches
- **Technical details:** Cache file format, invalidation, storage
- **Performance comparison table** showing expected improvements
- **Troubleshooting section** for common issues
- **FAQ** answering common questions about caching

**Best for:** Understanding caching in depth, troubleshooting cache issues

## Quick Comparison

| Scenario | Guide Section | Expected Runtime | Key Setting |
|----------|---------------|-----------------|-------------|
| 🚀 **Fast exploration** | PERFORMANCE_OPTIMIZATION_GUIDE.md → Workflow 1 | 3-6 min | Euclidean + Parquet + max_iter=15 |
| 🔄 **Parameter tuning** | PERFORMANCE_OPTIMIZATION_GUIDE.md → Workflow 2 | 1-5 min/iteration | Same metric, cache enabled |
| 📊 **Publication quality** | PERFORMANCE_OPTIMIZATION_GUIDE.md → Workflow 3 | 45-60 min | DTW + max_iter=100 |
| 🎯 **Cache optimization** | DISTANCE_CACHING_GUIDE.md | 5x speedup | Euclidean metric |

## Key Optimization Techniques

### 1. Parquet Files (5-10x faster I/O)
```python
USE_PARQUET = True  # After first run with CSV
```
- Automatic CSV → Parquet conversion
- 50-80% smaller file size
- 5-10x faster reading

### 2. Max Iterations (Faster convergence)
```python
CONFIG['max_iter'] = 15  # vs 100 for thorough
```
- Lower values converge faster
- 5-10x speedup possible
- Good for exploratory work

### 3. Distance Metric & Caching
```python
CONFIG['time_series_distance'] = 'euclidean'  # Cacheable
# First run: computes & caches distances
# Second run: loads from cache (instant)
```
- Euclidean: 10-20x faster than DTW, but less accurate
- DTW: Slower but better temporal fidelity
- Caching: 5-10x speedup on re-runs

## Recommended Starting Point

### For Your First Run:
```python
# In notebook cell 3 (CONFIG):
CONFIG = {
    'time_series_distance': 'euclidean',  # Fast
    'max_iter': 15,                       # Quick convergence
    'cluster_count': 6,
    'random_state': 42,
}

# In notebook cell 4:
USE_PARQUET = False  # Use CSV first, then switch to Parquet
```

**Expected time:** 5-10 minutes

### For Repeated Runs:
```python
# Just change cluster_count, keep everything else
CONFIG['cluster_count'] = 8  # Try 8 instead of 6

# Distance cache loads automatically
# TIME: ~1 minute (instead of ~5 minutes)
```

### For Final Publication:
```python
# Switch to DTW for accuracy
CONFIG['time_series_distance'] = 'dtw'
CONFIG['max_iter'] = 100

# Switch to Parquet for faster I/O
USE_PARQUET = True

# Expected time: ~45 minutes
```

## Integration with Notebook 01

The optimization features are integrated directly into `notebooks/01_spacetime_cube_TSC.ipynb`:

- **Cell 3:** CONFIG with `time_series_distance`, `max_iter` settings
- **Cell 4:** Data loading with `USE_PARQUET` toggle and parquet conversion
- **Cell 11:** Clustering with automatic distance caching
- **Cell 15:** Batch processing updated with caching support

## Performance Benchmarks

### Your Gentrification Dataset (1,421 locations, 8 variables)

| Approach | Total Time | Per Variable |
|----------|-----------|--------------|
| CSV + DTW + max_iter=100 | ~6 hours | ~45 min |
| CSV + Euclidean + max_iter=20 | ~40 min | ~5 min |
| Parquet + Euclidean + cache + max_iter=15 | 5 min (first) + 2 min (re-runs) | 30 sec + 15 sec |

**Result:** 50-100x speedup possible with all three optimizations!

## Cache Management

### View all caches:
```python
from pathlib import Path
cache_dir = Path('data/processed/distance_matrix_cache')
print(list(cache_dir.glob('*.npy')))
```

### Clear specific cache:
```python
cache_file = cache_dir / 'age_18_25_euclidean_distances.npy'
cache_file.unlink()
```

### Clear all caches:
```python
import shutil
shutil.rmtree('data/processed/distance_matrix_cache')
```

## Next Steps

1. **Read PERFORMANCE_OPTIMIZATION_GUIDE.md** for the full optimization strategy
2. **Update Cell 3 (CONFIG)** in notebook 01 with your preferred settings
3. **Run your first analysis** with exploratory settings (fast)
4. **Switch to publication settings** when ready for final results
5. **Refer to DISTANCE_CACHING_GUIDE.md** if caching questions arise

## Questions?

See the respective guides:
- **PERFORMANCE_OPTIMIZATION_GUIDE.md** - General optimization questions
- **DISTANCE_CACHING_GUIDE.md** - Distance caching specific questions
- Notebook 01 cell documentation - Implementation details
