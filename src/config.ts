/**
 * ==================================================================
 *  站点内容配置 —— 全站文字都在这个文件里改
 *  3D 轮播作品列表请编辑独立的 src/data/works.ts
 *  改完保存并推送 GitHub，Actions 会自动重新构建发布
 * ==================================================================
 */

/**
 * 站点根路径：构建时自动处理（个人主页仓库 <用户名>.github.io 为 "/"；
 * 普通仓库模式为 "/仓库名"），下载链接会自动拼上该前缀。
 */
const pubBase = import.meta.env.BASE_URL;

export const siteConfig = {
  // ---------------- 基本资料 ----------------
  /** 网站署名：页头 Logo / Hero / 页脚 */
  name: "游戏来",
  /** 职业标签 */
  title: "全栈开发者 · Full-Stack Developer",
  /** 站点简介（浏览器标签 / SEO） */
  description:
    "游戏来 的个人网站 —— 程序员作品展示、开源源码与软件免费下载。",

  /** 主题强调色：全站统一（十六进制） */
  accentColor: "#38bdf8",

  /**
   * 示例数据开关
   * demoMode = true 时：作品卡片标注「示例」徽标。
   * 填好真实信息后把这里改成 false 即可。
   */
  demoMode: true,

  // ---------------- 社交链接（留空 "" 则不显示） ----------------
  social: {
    email: "", // 例如 "you@example.com"
    linkedin: "", // 例如 "https://www.linkedin.com/in/you"
    twitter: "", // 例如 "https://x.com/you"
    github: "https://github.com/Mralai", // 你的 GitHub 主页
  },

  // ---------------- 关于我（每个元素是一段） ----------------
  aboutMe: [
    "我是一名程序员，专注于把想法变成稳定、易用的产品。",
    "这段文字目前是「示例数据」：在下方段落里填写你的真实介绍，可写多段，每段一个元素。",
  ],

  // ---------------- 下载中心（大文件建议放 GitHub Releases 后填直链） ----------------
  downloads: [
    {
      name: "yxl-devkit-demo",
      version: "1.0.0",
      platform: "Windows / macOS / Linux",
      size: "1 KB",
      url: `${pubBase}files/yxl-devkit-demo-1.0.0.zip`,
      desc: "示例安装包：演示「下载中心」的登记方式，内含使用说明；替换成你的真实包体即可。",
      isDemo: true,
    },
    {
      name: "site-theme-demo",
      version: "0.1.0",
      platform: "Web",
      size: "1 KB",
      url: `${pubBase}files/site-theme-demo.zip`,
      desc: "示例前端资源包。正式分发大文件（>50MB）建议使用 GitHub Releases 托管。",
      isDemo: true,
    },
  ],
};
