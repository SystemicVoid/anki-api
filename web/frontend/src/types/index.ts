export interface Card {
  front: string;
  back: string;
  context: string;
  tags: string[];
  source: string;
  deck: string;
  model: string;
}

export interface ValidationWarning {
  message: string;
  severity: 'error' | 'warning' | 'info';
}

export interface CardWithValidation {
  card: Card;
  warnings: ValidationWarning[];
  index: number;
  total: number;
}

export interface CardsFileResponse {
  filename: string;
  cards: CardWithValidation[];
  total: number;
}

export interface AnkiStatus {
  connected: boolean;
  error?: string;
}

export interface AddCardResponse {
  success: boolean;
  note_id?: number;
  error?: string;
}

export interface FileListResponse {
  files: string[];
}

export type ReviewAction = 'approve' | 'edit' | 'skip' | 'quit';
