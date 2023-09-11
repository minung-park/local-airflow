# local-airflow
로컬에서 dag 를 테스트하기 위한 repository 입니다.  
airflow 의 버전은 2.5.3 입니다.

소스 코드 구조는 다음과 같습니다.
```
.
|____dags  # 실제 DAG 스크립트들이 존재하는 폴더입니다. 해당 폴더의 파이썬 스크립트가 컴포저 스토리지에 업로드 됩니다.
| |____sample  # 컴포저 스토리지 내에서 스크립트를 분류하기 위한 폴더입니다. (필요에 맞게 커스텀 세팅!)
| | |____test.py
| |____dag_utils  # DAG 에서 공통적으로 사용되는 파일이 이 디렉토리 내에 존재합니다.
| | |____common.py
|____data  # 스크립트 실행에 필요한 데이터 파일을 넣어두는 디렉토리 입니다. (ex gcp-auth 등)
| |____auth.json
```

### pip packages 설치
```yaml
# docker-compose.yml 파일에서 필요한 패키지 정의(line 54)
_PIP_ADDITIONAL_REQUIREMENTS: ${_PIP_ADDITIONAL_REQUIREMENTS:- pycryptodome pymongo }
```

### GCP Composer 와의 비교
[composer user data 참고](https://cloud.google.com/composer/docs/composer-2/cloud-storage?hl=ko)  
composer 에서는 기본적으로 module path 가 다음과 같이 정의되어 있습니다.
- '/home/airflow/gcs/dags'
- '/etc/airflow/config'
- '/home/airflow/gcs/plugins'
- 이 외에 /opt/python3.8/bin, /opt/python3.8/lib 등이 있음  

위의 구조와 최대한 맞추기 위해 `dags` `plugins` `data` 디렉토리는 공유하도록 docker-compose 파일 수정
```yaml
  # docker-compose.yml 55번째 라인
  volumes:
    - ./dags:/opt/airflow/dags
    - ./logs:/opt/airflow/logs
    - ./plugins:/opt/airflow/plugins
    - ./data:/opt/airflow/data
```
이런 구조로 되어 있어 모듈을 임포트 하려면
dags/sample/test.py 의 경우
```python
from dag_utils import common
...(중략)
```
과 같이 스크립트 파일을 작성해야 하는데, 이렇게 하는 경우 pytest 할 때 모듈 에러가 남.  
dag 코드 내에서의 import 와 pytest 를 모두 가능하게 하기 위해 module path 에 
- composer 의 경우 `/home/airflow/gcs` 추가 필요
- local 의 경우 `dags의 상위 폴더` 추가 필요  
위 두 가지를 만족하기 위해 dag 스크립트에 아래와 같은 코드 추가
```python
import os
import sys

def get_path(_path, step, _dir=None):
    up_path = os.sep.join(_path.split(os.sep)[:-step])
    if _dir is None:
        return up_path
    return os.path.join(up_path, _dir)


module_path = get_path(os.path.dirname(os.path.abspath(__file__)), 2)  # 스크립트 파일을 기준으로 최상위 폴더를 모듈패스로 지정
sys.path.append(module_path)
```
