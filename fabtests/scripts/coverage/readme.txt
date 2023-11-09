Command option:

python ./gen_report.py -m <master_file_name>  -d <results_dir>  [-v <level>]

level:
No -v:  report total summary
-v 1:   report total summary plus per provider's summary
        (provider is any directory under "results_duir").
-v 2:   report level 1 plus features covered counts (0 -- not covered)
-v 3:   report level 2 plus detail tests info.

Example:
python ./gen_report.py -m ./master_features.json -d feature_coverage_logs -v 2
