# Lookup Benchmark tool
Simple tool to run benchmarks against the lookup endpoint.

## Usage
Run python3 with `./benchmark/benchmarks.py`.

### Parameters

| parameter | value | description |
|----|----|----|
|-e , --endpoint | ENDPOINT | Require, Lookup endpoint to test. Example https://www.endpoint.com/lookup |
|-d , --datafile | DATAFILE | Require, Sample Data file (csv) to load |
|-a , --auth | AUTHENTICATION | Optional, Authentication string. Default to env variable or ".env" file. |
|-w , --workers | MAX_WORKERS | Optional, Maximum number of workers default to 10 |
|-t , --threads | MAX_THREADS | Optional, Maximum number of threads, default to 20 |
|-s , --samples | MAX_SAMPLES | Optional, Maximum number of samples to run, default to 100 |

### Result
A result and summary `csv` file will be generated.

## Example usage
```
python3 ./benchmark/benchmarks.py -e "https://growth-lookup.herokuapp.com/lookup"  -d ./benchmark/data.csv
```

### Example Output
Results:
```
key,status,start_time,end_time,duration(s)
json2,200,05/21/2020 16:52:40,05/21/2020 16:52:41,0.4955141544342041
test1,200,05/21/2020 16:52:40,05/21/2020 16:52:41,0.7784969806671143
json6,200,05/21/2020 16:52:40,05/21/2020 16:52:41,0.6550769805908203
json3,200,05/21/2020 16:52:40,05/21/2020 16:52:41,0.5283188819885254
json2,200,05/21/2020 16:52:40,05/21/2020 16:52:41,0.5525898933410645
test1,200,05/21/2020 16:52:40,05/21/2020 16:52:41,0.8779909610748291
json5,200,05/21/2020 16:52:40,05/21/2020 16:52:41,0.46996593475341797
string3,200,05/21/2020 16:52:40,05/21/2020 16:52:41,0.8488237857818604
```

Summary:
```
status,total duration(s), total counts, average response(ms)
200,5075.892631,9999,507.640027
```