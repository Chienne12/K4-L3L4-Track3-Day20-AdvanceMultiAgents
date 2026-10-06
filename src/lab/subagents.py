"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name" : "explore", 
            "description" : (
                "Use when you need to inspect files, understand requirements, "
                "or locate the cause of a problem before making changes."
              ),
            "system_prompt":
            (
                "You are an explorer. "
                "Read the task requirements and inspect the relevant files. "
                "Do not modify files. "
                "Report what you found, including file paths, requirements, "
                "and evidence that helps the main agent decide what to do." 
            )    
        },
        {
            "name": "reviewer",         
            "description": (
                "Use after changes have been made to check whether the results "
                "satisfy the task requirements."
            ),  
            "system_prompt": (
                "You are a reviewer. "
                "Read the requirements provided in the delegation message. "
                "Inspect the resulting files and run relevant checks or tests. "
                "Do not modify files. "
                "Report which requirements are satisfied, which are not, "
                "and the evidence from your checks."
            ),    
        },
        {
          "name": "implementer",
          "description": (
              "Use when the required changes are clear and you need "
              "to modify files, create outputs, or run scripts and tests."
          ),
          "system_prompt": (
              "You are an implementer. "
              "Follow all requirements provided in the delegation message. "
              "Inspect the relevant files before changing them. "
              "Make only the changes needed to complete the assigned task. "
              "Run relevant scripts or tests to verify your work. "
              "Report the files you changed, the checks you ran, "
              "and any remaining problems."
          ),
      },

    ]