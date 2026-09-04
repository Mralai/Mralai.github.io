/**
 * ==================================================================
 *  首页 3D 作品轮播 · 独立作品数据配置
 *  以后新增 / 修改轮播作品：只改本文件，不需要动任何页面代码
 *  字段：
 *    slug    —— 唯一标识（同时用作下载包文件名）
 *    name    —— 作品名称
 *    desc    —— 一句简短简介
 *    media   —— 媒体预览：
 *                图片 { type:'image', src:'media/...' }
 *                视频 { type:'video', src:'远程或本地mp4', poster:'封面图' }
 *                （src/poster 相对于站点根路径填写即可，构建时自动拼前缀）
 *    pack    —— 资源包下载信息 { file, size, version }
 * ==================================================================
 */

export interface CarouselMedia {
  type: "image" | "video";
  src: string;
  /** 视频封面（缩略图），移动端优先展示它，点击播放后才加载视频 */
  poster?: string;
}

export interface CarouselPack {
  /** 下载文件路径（相对站点根），一般放 public/files/works/ 下 */
  file: string;
  size: string;
  version: string;
}

export interface CarouselWork {
  slug: string;
  name: string;
  desc: string;
  media: CarouselMedia;
  pack: CarouselPack;
}

export const carouselWorks: CarouselWork[] = [
  {
    slug: "auraflow",
    name: "auraflow · 深色主题方案库",
    desc: "覆盖 120+ 组件的设计令牌与主题方案，一键切换整套深色视觉。",
    media: {
      type: "image",
      src: "media/works/cover-coding.jpg",
    },
    pack: {
      file: "files/works/auraflow-demo.zip",
      size: "1 KB",
      version: "1.0.0",
    },
  },
  {
    slug: "devdock",
    name: "devdock · 开发者工具箱",
    desc: "多端统一的开发效率工具：环境管理、命令速查、一键脚本。",
    media: {
      type: "image",
      src: "media/works/cover-computer_programming.jpg",
    },
    pack: {
      file: "files/works/devdock-demo.zip",
      size: "1 KB",
      version: "0.9.2",
    },
  },
  {
    slug: "pulse-console",
    name: "pulse-console · 数据大屏引擎",
    desc: "拖拽搭建实时数据大屏，毫秒级渲染海量指标。（点击 ▶ 播放演示视频）",
    media: {
      type: "video",
      src: "https://videos.pexels.com/video-files/3129957/3129957-sd_960_540_25fps.mp4",
      poster: "media/works/picsum-tech-console-02.jpg",
    },
    pack: {
      file: "files/works/pulse-console-demo.zip",
      size: "1 KB",
      version: "1.2.0",
    },
  },
  {
    slug: "nitro-notes",
    name: "nitro-notes · 极简效率笔记",
    desc: "纯本地优先的笔记应用：Markdown、全局搜索、端到端加密同步。",
    media: {
      type: "image",
      src: "media/works/picsum-ui-dark-01.jpg",
    },
    pack: {
      file: "files/works/nitro-notes-demo.zip",
      size: "1 KB",
      version: "2.0.1",
    },
  },
];
