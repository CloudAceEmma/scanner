import git
import tempfile
import shutil
from .llm_analyzer import analyze_text_with_gemini


def parse_diff_for_snippet(diff_content, snippet):
    lines = diff_content.split("\n")
    file_path = None

    for i, line in enumerate(lines):
        if line.startswith("+++ b/"):
            file_path = line[6:]

        if line.startswith("+") and snippet.strip() in line[1:]:
            # Found the snippet. Now find the line number from the nearest hunk header.
            hunk_header_index = -1
            for j in range(i, -1, -1):
                if lines[j].startswith("@@ "):
                    hunk_header_index = j
                    break

            if hunk_header_index != -1:
                hunk_header = lines[hunk_header_index]
                parts = hunk_header.split(" ")
                try:
                    start_line = int(parts[2].split(",")[0][1:])

                    offset = 0
                    for k in range(hunk_header_index + 1, i + 1):
                        if not lines[k].startswith("-"):
                            offset += 1

                    line_number = start_line + offset - 1

                    return {
                        "file_path": file_path,
                        "line_number": line_number,
                        "snippet": line[1:].strip(),
                    }
                except (ValueError, IndexError):
                    continue  # Malformed hunk header
    return None


def get_repo_obj(repo_path_or_url):
    """Clones a remote repo or loads a local one."""
    if repo_path_or_url.startswith("http") or repo_path_or_url.startswith("git@"):
        temp_dir = tempfile.mkdtemp()
        git.Repo.clone_from(repo_path_or_url, temp_dir)
        return git.Repo(temp_dir), temp_dir
    else:
        return git.Repo(repo_path_or_url), None


def scan_repository(repo_path_or_url, commits_count):
    """
    Orchestrates the scanning process.
    """
    repo, temp_dir = get_repo_obj(repo_path_or_url)
    commits = list(repo.iter_commits(max_count=commits_count))
    all_findings = []

    for commit in commits:
        if not commit.parents:
            # Initial commit, diff against empty tree
            diff_content = repo.git.diff('4b825dc642cb6eb9a060e54bf8d69288fbee4904', commit.hexsha)
        else:
            parent = commit.parents[0]
            diff_content = repo.git.diff(parent.hexsha, commit.hexsha)
        commit_message = commit.message

        # Combine diff and message for a comprehensive analysis
        full_content = f"Commit Message:\n{commit_message}\n\nDiff:\n{diff_content}"

        analysis_result = analyze_text_with_gemini(full_content)

        if analysis_result and "snippet" in analysis_result:
            location_info = parse_diff_for_snippet(
                diff_content, analysis_result["snippet"]
            )
            if location_info:
                finding = {
                    "commit_hash": commit.hexsha,
                    **location_info,
                    "finding_type": analysis_result.get("finding_type"),
                    "rationale": analysis_result.get("rationale"),
                    "confidence": analysis_result.get("confidence"),
                }
                all_findings.append(finding)

    if temp_dir:
        shutil.rmtree(temp_dir)  # Clean up cloned repo
    return all_findings
