// @ts-check
import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";

/**
 * 部署路径自动适配：
 *  - 个人主页仓库（<用户名>.github.io）：base 为 "/"（默认，无需设置）
 *  - 普通仓库（GitHub Pages 项目站点）：由 CI 传入 BASE_PATH=/仓库名
 *  - 本地开发 / 自定义服务器：保持 "/" 即可
 */
const base = process.env.BASE_PATH || "/";

export default defineConfig({
  base,
  vite: {
    plugins: [tailwindcss()],
  },
});
