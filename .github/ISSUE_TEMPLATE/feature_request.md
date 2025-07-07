name: Feature Request
description: Suggest an idea for this project.
title: "[FEATURE] "
labels: enhancement
assignees: ''

body:
  - type: markdown
    attributes:
      value: |
        Thank you for suggesting a new feature! Please fill out the details below.

  - type: input
    id: summary
    attributes:
      label: Feature Summary
      description: What would this feature do?
      placeholder: Brief description of the feature
    validations:
      required: true

  - type: textarea
    id: motivation
    attributes:
      label: Why is this needed?
      description: What problem does this feature solve or improve?
    validations:
      required: true

  - type: textarea
    id: details
    attributes:
      label: Feature Details
      description: How should it work? Include examples if possible.
