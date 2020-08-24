# gitlab-server-hook
pre-receive hook which check certain commit convention

# 현재 체크하는 컨벤션

- target branch 의 server 의 HEAD 이후로 쌓인 커밋 목록의 타이틀이 모두 다음 중 하나로 시작하는지
  - `[New Feature]`, `[BugFix]`, `[Refactor]`, `[Style]`, `[Documentation]`, `[TypoFix]`
  - 띄어쓰기 구분 없으며, 대소문자는 구분
- 해당 부분은 코드 내의 regex 를 수정하여 사용하실 수 있습니다. 
  
# 확인 필요 리스트(TODO)
1) new branch 의 경우 쌓인 모든 커밋을 체크하게 되어 일단은 아예 skip 처리해두었으나 어느 커밋부터 체크해야하는지 어케 결정해야 할 지 모르겠음
    - new branch 는 base 가 없음
2) 브랜치 삭제의 경우 push event 인지 확실하지 않음
3) commit msg 까지 체크를 위한 커맨드
    - `git rev-list --first-parent a9aef22ba399b9d85bba92d023dadc8004a773b6...ae38b75beb2205eedcc1c98e38407a6a6c72d889 --format=format:"Hash :%n%h%nTitle : %n%s%nMsg : %n%b"`

# 확인된 리스트
1) commit 여러 개 한 번에 push 할 경우 모든 커밋 체크
    - server 의 해당 브랜치의 HEAD commit (base) 기준으로 그 위에 쌓인 모든 커밋
2) 이미 서버에 반영되어있던 커밋(base 이전 커밋들)은 체크에서 제외
3) rebase 후 forced push 의 경우 상관없음