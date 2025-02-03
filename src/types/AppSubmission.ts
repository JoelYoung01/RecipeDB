export type AppSubmission = {
  id: number;
  status: number;
  created_by: number;
  created_on: string;
  link: string | null;
};

export type AppSubmissionDetail = {
  id: number;
  status: number;
  created_by: number;
  created_on: string;
  app_definition_id: number;
  link: string | null;
};
