# to-do
- JobService.cleanup_old_jobs을 주기적으로 트리거 하도록 리팩토링.

- PADDLE_WEBHOOK_SECRET 발급


# done
- 모든 메서드에 worspace_path, config_path가 필요한건 아니지 않음?

- _get_ref_audio 메서드의 역할과 용도가 뭔지?

- dubbingservice에서는 s3에 있는 영상을 다운, 업로드 하기.

- ai 모듈에서 안 쓰는 기능 전부 제거 - ✅ whisperx local 제거 완료

- AI 모듈들: 순수한 데이터 처리 로직
    - 입력 받은 파일을 처리하고 결과 반환
    - 파일 경로는 매개변수로 받기

- dubbing_service.py: 오케스트레이션 & 인프라
    - 작업공간 관리
    - 파일 입출력 관리  
    - 진행률 추적
    - 에러 처리 & 알림
    - 결과물 업로드

- dubbing_service에서 왜 알림 이메일 보내는 기능 없앴어?

- s3_bucket, s3_key, thumbnail_url, duration, file_size, format, resolution, fps, extra_metadata 칼럼을 media_files 테이블로 옮겨. 올긴 후 관련 코드도 이에 맞게 수정해. 예를 들면 dubbing_service 등 video.s3_key를 직접 참조하는 코드가 있어, “원본”을 가져올 때 MediaFile(file_type='original') 조회로 교체하는거지.

- 장기적으로는 산출물 경로를 MediaFile에 표준화하는 리팩터링

- @storage_service.py에 추가한 메서드와 기존에 있던 메서드와 무슨 차이?

- dubbing, storage, video 세가지 서비스에서 겹치는 메서드 리팩토링

- 그 외 서비스 파일들과의 리팩토링할 게 있나 판단.

- dubbing서비스 파일에 있는 알림 메서드를 알림 파일로 이동?

- smpt 사용법과 관련 코드 이해.

- EB를 2개 사용. 하나는 웹서버환경, 다른 하나는 작업자 환경.
    세부사항:
    백엔드 api 서버는 웹서버 환경 ec2 이용.
    영상더빙프로세스는 작업자 환경 ec2 이용.
    영상더빙프로세스의 메세징 큐는 sqs 사용.
    데이터베이스는 rds 사용.
    원본 영상과 결과 파일들은 s3에 저장.
    smtp는 ses 사용.
    log는 Amazon CloudWatch 사용.
    개발자 알림은 Amazon SNS 사용.
    사용자 정의 도메인 연결은 Amazon Route 53 사용.

- watchtower 기능 삭제, smtp 기능 삭제.

- message_models.py도 model/ 파일로 들어가야하는 거 아님?

- api endpoint, service layer 두 사이 간에 빼먹은게 없나

- api endpoint의 실패 오류 코드가 없는 건 왜 그런지? 오류 코드를 라이브러리를 써서 간편하게 표현하는게 어떤지

- elevenlabs 코드 파일 이해한 후, openai 코드 파일 생성하기.

- @openai_asr.py에서 오디오 슬라이스 기능이 꼭 필요한건지, 지울 수는 없는지

- JobService.get_jobs_by_user / get_job를 사용하는 엔드포인트 추가

- 앱 시작 시 중단 작업 복구 로직 리팩토링
    - 현재는 ice.get_pending_jobs(job_type="dubbing")로 “pending”만 조회.
    - 이를 status가 processing 이거나 pending 이면 복구하도록 리팩토링.

- DubbingService.resume_dubbing_pipeline을 사용하는 엔드포인트 추가
    - 사용자가 실패/중단 작업을 “재시작”할 API 추가
    
- strip를 paddle로 교체

