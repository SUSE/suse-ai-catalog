{{/*
Expand the name of the chart.
*/}}
{{- define "litellm-registry.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "litellm-registry.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Resolve the Secret name that stores LITELLM master key.
*/}}
{{- define "litellm-registry.masterSecretName" -}}
{{- if .Values.litellm.existingSecretName -}}
{{- .Values.litellm.existingSecretName -}}
{{- else -}}
{{- printf "%s-master-key" (include "litellm-registry.fullname" .) -}}
{{- end -}}
{{- end }}
