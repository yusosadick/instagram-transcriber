export type JobStatus =
  | "queued"
  | "downloading"
  | "extracting_audio"
  | "transcribing"
  | "exporting"
  | "completed"
  | "failed"
  | "cancelling"
  | "cancelled";

export interface JobResponse {
  id: string;
  status: JobStatus;
}

export interface JobError {
  code: string;
  message: string;
}

export interface JobStatusResponse {
  id: string;
  status: JobStatus;
  stage_message: string;
  progress_percent: number;
  error: JobError | null;
}

export interface TranscriptWord {
  start: number;
  end: number;
  word: string;
}

export interface TranscriptSegment {
  start: number;
  end: number;
  text: string;
  words: TranscriptWord[];
}

export interface TranscriptResult {
  segments: TranscriptSegment[];
  language: string;
  language_probability: number;
  duration: number;
  word_count: number;
  text: string;
  model_size: string;
  device: string;
}

export interface HistoryItem {
  id: string;
  source_type: "url" | "file";
  source: string;
  title: string;
  created_at: string;
  duration: number;
  word_count: number;
  language: string;
}

export interface HealthResponse {
  status: string;
  ffmpeg: boolean;
  device: string;
  compute_type: string;
}

export type ExportFormat = "txt" | "srt" | "json";
