export interface PrintRequest {
  assignedTo: string;
  taskName: string;
  taskDesc: string;
  createdAt: Date;
  url: string;
  fact: string;
}

export interface UselessFact {
  id: string;
  text: string;
  source: string;
  source_url: string;
  language: string;
  permalink: string;
}