/**
 * ==================================================================
 *  站点内容配置 —— 全站所有文字 / 作品 / 下载 / 经历都在这个文件里改
 *  改完保存并推送 GitHub，Actions 会自动重新构建发布
 * ==================================================================
 */

/**
 * 站点根路径：构建时自动处理（个人主页仓库 <用户名>.github.io 为 "/"；
 * 普通仓库模式为 "/仓库名"），下载链接会自动拼上该前缀。
 */
const pubBase = import.meta.env.BASE_URL;

export interface ProjectItem {
  name: string;
  description: string;
  skills: string[];
  /** GitHub 仓库地址（显示「源码」按钮） */
  github?: string;
  /** 在线体验地址（显示「在线体验」按钮） */
  demo?: string;
  /** 直接下载地址（显示「下载 xx」按钮）；大文件请用 GitHub Releases */
  download?: string;
  /** true = 卡片上标注「示例数据」 */
  isDemo?: boolean;
}

export interface DownloadItem {
  name: string;
  version: string;
  platform: string;
  size: string;
  url: string;
  desc: string;
  isDemo?: boolean;
}

export const siteConfig = {
  // ---------------- 基本资料 ----------------
  /** 网站署名：页头 Logo / Hero / 页脚 */
  name: "游戏来",
  /** 职业标签 */
  title: "全栈开发者 · Full-Stack Developer",
  /** 站点简介（浏览器标签 / SEO） */
  description:
    "游戏来 的个人网站 —— 程序员作品展示、开源源码与软件免费下载。",
  /** Hero 口号（一段话即可） */
  heroTagline: "用代码把想法变成可以运行的产品 —— 这里是作品集与下载站。",

  /** 主题强调色：全站统一（十六进制） */
  accentColor: "#38bdf8",

  /**
   * 示例数据开关
   * demoMode = true 时：页面展示「示例数据」占位内容，便于对照填写。
   * 把你的真实信息填好之后，把这里改成 false 即可。
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

  // ---------------- 技术栈标签 ----------------
  skills: [
    "JavaScript / TypeScript",
    "Node.js",
    "Python",
    "React",
    "Vue",
    "HTML / CSS",
    "Git",
    "Docker",
    "Linux",
  ],

  // ---------------- 作品集（isDemo: true 会标注「示例数据」） ----------------
  projects: [
    {
      name: "本站：深色科技风个人作品站",
      description:
        "你现在看到的这个网站：基于开源模板 DevPortfolio（Astro + Tailwind CSS，MIT 协议）深度定制 —— 深色科技风、中文排版优化、单文件内容配置、内置下载中心，GitHub Actions 自动发布。",
      skills: ["Astro", "Tailwind CSS", "TypeScript", "GitHub Actions"],
      github: "https://github.com/Mralai/Mralai.github.io",
    },
    {
      name: "示例作品 · 终端工具箱 terminal-toolkit",
      description:
        "示例条目：用于演示「作品卡片」的展示效果。把你的真实作品按同样的结构填进 src/config.ts 即可，支持源码 / 在线体验 / 直接下载三种按钮。",
      skills: ["Go", "CLI", "跨平台"],
      isDemo: true,
    },
    {
      name: "示例作品 · 效率桌面工具 deskgo",
      description:
        "示例条目：用于演示带下载按钮的作品卡片。正式作品请替换本条目，并把安装包放入 public/files/ 或发布到 GitHub Releases。",
      skills: ["Electron", "React", "Node.js"],
      isDemo: true,
    },
  ],

  // ---------------- 下载中心 ----------------
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

  // ---------------- 经历 ----------------
  experience: [
    {
      title: "全栈开发工程师（示例）",
      company: "示例科技公司",
      dateRange: "2023.06 – 至今",
      bullets: [
        "负责核心业务模块的前后端开发与维护（示例数据，请替换为真实经历）",
        "参与服务架构优化，接口平均响应时间下降 40%（示例数据）",
        "推动团队代码规范与 CI/CD 落地（示例数据）",
      ],
      isDemo: true,
    },
    {
      title: "前端开发（示例）",
      company: "示例工作室",
      dateRange: "2021.09 – 2023.05",
      bullets: [
        "基于 React 技术栈开发多个业务系统（示例数据）",
        "搭建组件库与主题规范，提升开发效率（示例数据）",
      ],
      isDemo: true,
    },
  ],

  // ---------------- 教育 ----------------
  education: [
    {
      school: "示例大学",
      degree: "计算机科学与技术 · 本科",
      dateRange: "2019 – 2023",
      achievements: [
        "系统学习数据结构、操作系统、计算机网络等核心课程（示例数据）",
        "毕业设计：基于 Web 的某某管理系统（示例数据）",
      ],
      isDemo: true,
    },
  ],
};
