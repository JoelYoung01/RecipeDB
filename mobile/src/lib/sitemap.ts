/**
 * Mobile mirror of the web app's src/sitemap.ts — tab bar + add-menu source
 * of truth. Keep aligned with SITE_MAP.md when routes change.
 */

export const paths = {
  login: "/login",
  register: "/register",
  verifyEmail: "/verify-email",
  home: "/home",
  recipes: "/recipes",
  recipeNew: "/recipes/new",
  recipeImport: "/recipes/import",
  recipeDetail: (id: number | string) => `/recipes/${id}`,
  recipeEdit: (id: number | string) => `/recipes/${id}/edit`,
  planner: "/planner",
  plannerFill: "/planner/fill",
  list: "/list",
  account: "/account"
} as const;

export type AddMenuActionId =
  | "import-link"
  | "import-photo"
  | "recipe-scratch"
  | "plan-meal"
  | "shop-item";

export interface AddMenuAction {
  id: AddMenuActionId;
  title: string;
  description: string;
  href: string;
  group: "create" | "quick";
  highlighted?: boolean;
  /** When true, UI may show a stub / coming-soon treatment */
  stub?: boolean;
}

export const addMenuActions: AddMenuAction[] = [
  {
    id: "import-link",
    title: "Import from link",
    description: "Paste a URL, we pull the recipe",
    href: `${paths.recipeImport}?method=link`,
    group: "create",
    highlighted: true,
    stub: true
  },
  {
    id: "import-photo",
    title: "Scan a photo",
    description: "Cookbook page or handwritten card",
    href: `${paths.recipeImport}?method=photo`,
    group: "create",
    stub: true
  },
  {
    id: "recipe-scratch",
    title: "Write from scratch",
    description: "Blank recipe form",
    href: paths.recipeNew,
    group: "create"
  },
  {
    id: "plan-meal",
    title: "Add meal to plan",
    description: "Pick a day, pick a recipe",
    href: paths.planner,
    group: "quick"
  },
  {
    id: "shop-item",
    title: "Grocery list",
    description: "Ingredients for the next 7 days",
    href: paths.list,
    group: "quick"
  }
];
