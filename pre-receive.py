#!/usr/bin/env python3
"""
Check Commit Convention As Gitlab server with pre-receive hook
"""
import re
import subprocess
import sys


def refactor_hash(commit_hash):
  """make hash value prettier"""
  if commit_hash.find('\'') != -1:
    return commit_hash.split('\'')[1]

  if commit_hash.find('\"') != -1:
    return commit_hash.split('\"')[1]

  return commit_hash


def inspect_commit(commit_hash, title):
  """decide skip or accept or reject for commit_title"""
  # 1) skip merge commit
  pattern_merge_commit = r'Mergebranch'
  compiled_pattern_merge_commit = re.compile(pattern_merge_commit,
                                             re.I | re.MULTILINE)
  match_merge_commit = re.match(compiled_pattern_merge_commit,
                                title)
  if match_merge_commit is not None:
    print("Skip If Merge Commit !!!!")
    return True, False

  # 2) skip revert commit
  pattern_revert_commit = r'Revert'
  compiled_pattern_revert_commit = re.compile(pattern_revert_commit,
                                              re.I | re.MULTILINE)
  match_revert_commit = re.match(compiled_pattern_revert_commit,
                                 title)
  if match_revert_commit is not None:
    print("Skip If Revert Commit !!!!")
    return True, False

  # TODO skip cherry-pick commit ?

  # 3) check commit title convention
  # TODO Also check for commit msg
  # TODO [New Feature, Refactor] 처럼 두 개 겹치는 경우 고려 필요?
  pattern_tag = r'\[(NewFeature|BugFix|Refactor|Style|Documentation|TypoFix)\]'
  compiled_pattern_merge_commit = re.compile(pattern_tag,
                                             re.I | re.MULTILINE)
  match_tag = re.match(compiled_pattern_merge_commit,
                       title)
  if match_tag is None:
    print("Commit %s is Invalid !!!!" % commit_hash)
    return False, True

  # If commit is valid
  print("Commit %s is Valid !!!!" % commit_hash)
  return False, False


def check_convention():
  """check if commit violate the commit convention"""
  all_ok = True

  # input_lines 의 원소는 다음과 같은 포맷의 스트링
  # {server 의 해당 브랜치의 HEAD commit} {push 한 client 의 해당 브랜치의 HEAD commit} {refs/heads/{$branch_name}}
  # 예)
  # c9a6a4acffb591a16e395d2ace4467260aec5276 61296afd28c0abc624aea79ebc5f099540416b65 refs/heads/asd
  for each_line in input_lines:  # TODO input_lines 는 지금까지 확인된 바로는 원소 하나인 경우만 존재하지만, 그렇지 않을 수도?
    if each_line:
      print("Content: " + each_line)
      (base, commit, ref) = each_line.strip().split()

      # skip if tags
      if ref[:9] == "refs/tags":
        # tag 생성의 경우 commit 이 새로 추가되는 게 아니므로 commit check 는 skip 설정
        all_ok = True
        continue

      # TODO new branch 처리
      if base == "0000000000000000000000000000000000000000":
        print("Skip If New Branch !!!!")
        # TODO new branch 의 경우 git rev-list 는 에러 발생
        # ```
        # kjy@kjy-ubuntu:~/temp/gityml/project1$  git rev-list --oneline --first-parent 0000000000000000000000000000000000000000...731cbd079a56f4a0e1578938c39e4792b9162bbe
        # fatal: Invalid symmetric difference expression 0000000000000000000000000000000000000000...731cbd079a56f4a0e1578938c39e4792b9162bbe
        # ```
        all_ok = True
        continue

      # subprocess 로 git rev-list 날려서 base 부터 commit 까지의 모든 commit title 을 조회
      revs = base + "..." + commit
      proc = subprocess.Popen(
        ['git', 'rev-list', '--oneline', '--first-parent', revs],
        stdout=subprocess.PIPE)

      all_commits_from_base = proc.stdout.readlines()
      # 다음 형태의 string 배열
      # ```
      # kjy@kjy-ubuntu:~/temp/gityml/project1$ git rev-list --oneline --first-parent 61296afd28c0abc624aea79ebc5f099540416b65...6e82a96b8cc387442852f05759c9302322c4daf1
      # 6e82a96 [commit2]  commit title
      # 917f692 [tag2] asdf
      # ```

      print("Start checking commits from HEAD")
      if all_commits_from_base:
        for commit_with_title in all_commits_from_base:
          item = str(commit_with_title)

          # get commit hash
          commit_hash = item.split()[0]
          commit_hash = refactor_hash(commit_hash)

          # get commit title
          commit_title = item.split()[1:]

          print(
            "With pre-receive hook, Check For Commit : %s, With Title : %s" % (
              commit_hash, commit_title))

          title_without_empty_space = "".join(commit_title)

          # Check Convention
          need_skip, is_invalid_commit = inspect_commit(
            commit_hash, title_without_empty_space)
          if need_skip:
            continue
          if is_invalid_commit:
            all_ok = False
            break

  return all_ok


if __name__ == "__main__":
  input_lines = sys.stdin.readlines()
  accept = check_convention()

  reject_msg = """
#########################################################################
[From the GitLab master] One of your commits didn't keep the convention.
[From the GitLab master] Please edit your commit title to follow the convention.
#########################################################################
"""
  if not accept:
    print(reject_msg)
    sys.exit(1)

  sys.exit(0)
