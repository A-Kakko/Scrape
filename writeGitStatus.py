import subprocess
from typing import List, Dict, Any, Tuple, Optional

def get_git_status() -> Dict[str, Any]:
    """
    Gitの状態を取得する関数

    Returns:
        Dict[str, Any]: Git状態の情報を含む辞書
    """
    result: Dict[str, Any] = {}
    
    try:
        # 現在のブランチを取得
        branch_cmd: List[str] = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        branch: str = subprocess.check_output(branch_cmd).decode('utf-8').strip()
        result["current_branch"] = branch
        
        # 変更ファイルの状態を取得
        status_cmd: List[str] = ["git", "status", "--porcelain"]
        status_output: str = subprocess.check_output(status_cmd).decode('utf-8')
        
        modified_files: List[str] = []
        staged_files: List[str] = []
        untracked_files: List[str] = []
        
        for line in status_output.splitlines():
            if line.startswith("M "):
                staged_files.append(line[2:])
            elif line.startswith(" M"):
                modified_files.append(line[2:])
            elif line.startswith("??"):
                untracked_files.append(line[3:])
            elif line.startswith("A "):
                staged_files.append(f"(新規) {line[2:]}")
        
        result["modified_files"] = modified_files
        result["staged_files"] = staged_files
        result["untracked_files"] = untracked_files
        
        # 最近のコミット履歴を取得
        log_cmd: List[str] = ["git", "log", "--oneline", "-n", "5"]
        log_output: str = subprocess.check_output(log_cmd).decode('utf-8')
        result["recent_commits"] = log_output.splitlines()
        
        return result
    
    except subprocess.CalledProcessError as e:
        return {"error": f"Gitコマンドの実行中にエラーが発生しました: {str(e)}"}
    except Exception as e:
        return {"error": f"予期せぬエラーが発生しました: {str(e)}"}

if __name__ == "__main__":
    status_info: Dict[str, Any] = get_git_status()
    
    print("=== Git状態情報 ===")
    print(f"現在のブランチ: {status_info.get('current_branch', 'エラー')}")
    
    print("\n変更済み（未ステージング）:")
    for file in status_info.get("modified_files", []):
        print(f"  - {file}")
    
    print("\nステージング済み:")
    for file in status_info.get("staged_files", []):
        print(f"  - {file}")
    
    print("\n未追跡ファイル:")
    for file in status_info.get("untracked_files", []):
        print(f"  - {file}")
    
    print("\n最近のコミット:")
    for commit in status_info.get("recent_commits", []):
        print(f"  {commit}")