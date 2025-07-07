name: Bug Report
description: Found a bug? Please help us improve by reporting it here.
title: "[BUG] "
labels: bug
assignees: ''

body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to fill out this bug report!

  - type: file
    id: log_file
    attributes:
      label: Log File
      description: |
        Upload relevant log file. 
        You can find log files in your ~/.local/share/nottodbox/logs folder in Linux, 
        ~/Library/Application Support/nottodbox/logs folder in macOS and
        C:/Users/<USER>/AppData/Local/nottodbox/logs folder in Windows.
      multiple: true
    validations:
      required: true

  - type: textarea
    id: steps
    attributes:
      label: Steps to Reproduce
      description: Please provide clear steps so we can reproduce the issue.
      placeholder: |
        1. Go to '...'
        2. Click on '...'
        3. Scroll down to '...'
        4. See the error
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What did you expect to happen?
    validations:
      required: true

  - type: textarea
    id: actual
    attributes:
      label: Actual Behavior
      description: What actually happened?
    validations:
      required: true

  - type: textarea
    id: extra
    attributes:
      label: Additional Information (like Screenshots)
      description: Include any other details like screenshots.