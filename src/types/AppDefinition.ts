import type { AppSubmission } from "./AppSubmission";
import type { Requirement } from "./Requirement";

export type AppDefinition = {
  id: number;
  name: string;
  start_date: string;
  due_date: string;
  description: string;
  status: AppDefinitionStatus;
  requirements: Requirement[];
  submissions: AppSubmission[];
};

export type AppDefinitionDashboard = {
  id: number;
  name: string;
  start_date: string;
  due_date: string;
  description: string;
  status: AppDefinitionStatus;
};

export enum AppDefinitionStatus {
  Active = 10,
  Complete = 20,
  Future = 30
}
