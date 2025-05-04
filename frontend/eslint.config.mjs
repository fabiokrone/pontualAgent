import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

// Configurações base do ESLint para Next.js
const nextConfig = compat.extends("next/core-web-vitals", "next/typescript");

// Configurações personalizadas para resolver problemas específicos
const customConfig = {
  files: ["**/*.{js,jsx,ts,tsx}"],
  rules: {
    // Regras gerais do ESLint
    "no-unused-vars": "warn",
    
    // Desativa regras de tipagem temporariamente enquanto estamos corrigindo
    "@typescript-eslint/no-explicit-any": "warn",
    "@typescript-eslint/no-implicit-any": "warn",
  },
  // Remove opções obsoletas
  languageOptions: {
    parserOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      ecmaFeatures: {
        jsx: true,
      },
    },
  },
  // Ignora arquivos específicos
  ignores: ["node_modules/**", ".next/**", "out/**", "dist/**"],
};

const eslintConfig = [
  ...nextConfig,
  customConfig,
];

export default eslintConfig;