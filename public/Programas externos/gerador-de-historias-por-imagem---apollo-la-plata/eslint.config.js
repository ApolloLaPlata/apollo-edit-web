import js from "@eslint/js";
import tseslint from "typescript-eslint";
import reactPlugin from "eslint-plugin-react";

export default tseslint.config(
  { ignores: ["dist/**"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["**/*.{ts,tsx}"],
    plugins: {
      react: reactPlugin,
    },
    rules: {
      "react/react-in-jsx-scope": "off",
      "@typescript-eslint/no-explicit-any": "off",
      "@typescript-eslint/no-unused-vars": "warn",
    },
    languageOptions: {
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
  }
);
