# Cloud Migration Input Data Script

The [cloud-migration-input-data.sh](cloud-migration-input-data.sh) script facilitates gathering crucial user inputs essential for cloud migration 
tasks. Users are prompted to provide information such as High Availability (HA) configuration and OnPrem region. 

Initially developed with interactive prompts, this approach led to confusion among customers. Consequently, the 
[jpd-data-collection.sh](jpd-data-collection.sh) script was introduced to streamline the process, enabling one-shot execution without any user inputs.


**Improvement**: 
- Introduced [jpd-data-collection.sh](jpd-data-collection.sh) script to eliminate user inputs and  streamline execution. So use that instaed .
- Also to *Compare configurations between two JFrog Platform Deployments (JPDs)*  
 please use the  [compare_2_jpd_configs.py](../jf-transfer-migration-helper-scripts/compare_2_jpd_configs_for_drift/compare_2_jpd_configs.py) as mentioned in [readme.md](jf-transfer-migration-helper-scripts/compare_2_jpd_configs_for_drift/readme.md)