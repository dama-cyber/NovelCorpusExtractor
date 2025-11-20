import type { ProcessPayload, ProcessResponse, WorkflowStageSnapshot } from '../types'

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

export async function mockProcessNovel(payload: ProcessPayload): Promise<ProcessResponse> {
  await delay(900)

  const workflowEntries = {
    reader: {
      id: 'reader',
      label: 'Reader · 分块',
      status: 'completed',
      detail: '完成 12 个文本块的语义切分',
      durationMs: 1600,
    },
    scanner: {
      id: 'scanner',
      label: 'Scanner · 语义预检',
      status: 'completed',
      detail: '完成异常字符清洗与章节标题对齐',
      durationMs: 600,
    },
    extractor: {
      id: 'extractor',
      label: 'Extractor · 事实抽取',
      status: 'completed',
      detail: 'Frankentexts 检索 + 结构化信息抽取',
      durationMs: 1800,
    },
    analyst: {
      id: 'analyst',
      label: 'Analyst · 深度提取',
      status: 'completed',
      detail: '抽取世界观、人物与冲突线',
      durationMs: 3200,
    },
    planner: {
      id: 'planner',
      label: 'Planner · 剧情规划',
      status: 'completed',
      detail: '生成三幕式剧情与章节骨架',
      durationMs: 2100,
    },
    archivist: {
      id: 'archivist',
      label: 'Archivist · 记忆体',
      status: 'completed',
      detail: '写入 YAML 记忆体与伏笔表',
      durationMs: 1400,
    },
    stylist: {
      id: 'stylist',
      label: 'Stylist · 文风增强',
      status: 'running',
      detail: '统一主角口吻，增强动作描写',
      durationMs: 1200,
    },
    creative: {
      id: 'creative',
      label: 'Creative Workflow',
      status: payload.runCreativeFlow ? 'completed' : 'pending',
      detail: payload.runCreativeFlow ? '10 个创作工具完成优化' : '未启用',
      durationMs: payload.runCreativeFlow ? 4100 : undefined,
    },
  } satisfies Record<string, WorkflowStageSnapshot>

  const workflowSummary = payload.runCreativeFlow
    ? {
        creationFlow: {
          opening: {
            logline: '三日倒计时 + 天幕裂痕 + 逆脉血统的悬疑玄幻开篇。',
            full_opening:
              '凌晨三点，巨城天幕被稀薄的紫色电弧撕出裂痕。被淘汰的演武少年被迫站在裂口下，耳边却响起迟到的系统提示音：距离天幕崩塌，还有 72 小时。',
          },
          chapterTitles: {
            titles: ['《裂幕三日》', '《记忆体走私者》', '《天命叛徒观察手册》'],
            tone: '悬疑 · 末世 · 快节奏',
          },
          commercial: {
            summary: '「三日倒计时 + 记忆体篡改 + 蜂群智能体」的高强度玄幻赛博感爽文。',
            highlights: ['钩子密集', '存在“叛徒即家人”的反转伏笔'],
          },
          platformAdaptation: {
            target_platform: '番茄',
            score: 86,
            adapted: '命名、简介、标签均已对齐番茄爽感策略，前三章保留双反转。',
          },
          hookDiagnostics: '建议在 3k 字内抛出“叛徒即家人”反转，钩子评分 8.8/10。',
        },
        optimizationFlow: {
          emotionDashboard: {
            pattern: 'wave',
            summary: '首章 2 次高潮点，建议在第 4 章补充情绪回落，防止读者疲劳。',
          },
          characterIssues: {
            issues: ['主角心声段落一二章语气不一致，需要统一成冷幽默'],
          },
          foreshadowingReport: {
            reminders: ['第2章提到的“逆脉铭纹”务必在第8章兑现'],
            overdue: [],
          },
          foreshadowingSchedule: [{ chapter: 8, action: '逆脉铭纹兑现' }],
          endingAnalysis: {
            pitches: [
              '主角化身天幕备份，保留自我意识并重启世界',
              '系统本体即主角未来自我，完成自我博弈闭环',
            ],
            risk: '注意别落入“系统操控一切”的老梗',
          },
          worldviewConflicts: {
            conflicts: ['宗门议会与城市管理局对“天幕起源”的描述不一致'],
          },
          agentSummarySample: [
            { agent: 'Analyst', highlight: '12 条人物线索 · 18 条冲突摘要' },
            { agent: 'Archivist', highlight: '输出 4 份记忆体 YAML · 1 份伏笔表' },
          ],
        },
        detectionFlow: {
          ai_likelihood: 'Medium',
          strategy: 'structure_shift',
          intensity: 'medium',
          evasion_preview:
            '通过不等长段落 + 多视角穿插，检测命中率下降 37%。章节引入“Frankentexts”专有名词，进一步降低相似度。',
        },
      }
    : undefined

  return {
    chunkResults: [
      {
        chunkId: 'chunk-001',
        title: '巨城天幕撕裂',
        summary:
          '主角在即将被淘汰的演武现场觉醒古老血脉，受困于家族与宗门双重博弈，意外触发天幕裂痕的第一丝波动。',
        tokens: 1534,
        themes: ['血脉觉醒', '宗门博弈', '末日征兆'],
        hookScore: 0.86,
      },
      {
        chunkId: 'chunk-002',
        title: '系统低语',
        summary:
          '系统在脑海中播报任务，要求在三日内锁定真正的“天命叛徒”，并以人物记忆体的形式抹除其存在感。',
        tokens: 1477,
        themes: ['系统倒计时', '疑似叛徒', '记忆体篡改'],
        hookScore: 0.79,
      },
    ],
    workflowStages: workflowEntries,
    workflow: workflowSummary,
    outline: [
      '第一幕：巨城被选者试炼失控，主角觉醒“逆脉”。',
      '第二幕：系统抹除记忆体，主角通过伏笔重建真相。',
      '第三幕：蜂群拓扑激活，众多智能体共同对抗失控的天幕。',
    ].join('\n'),
    memories: [
      {
        id: 'worldview',
        title: '世界观记忆体',
        entries: [
          '巨城依赖天幕维系，裂痕与古老“逆脉”血统相关。',
          '存在三大势力：宗门议会、城市管理局、地下Frankentexts走私者。',
        ],
      },
      {
        id: 'characters',
        title: '人物记忆体',
        entries: [
          '主角：表面懒散，实为伏笔收藏家，语言风格偏冷幽默。',
          '师姐：白天是分析师，夜晚化身Hook优化器，语速极快。',
        ],
      },
    ],
    creative: payload.runCreativeFlow
      ? {
          openingScene:
            '某日凌晨三点，巨城上空的天幕被一道紫色裂痕撕开。主角在废弃的第七演武场醒来，耳边是系统迟到的提示音。',
          titles: ['《裂幕三日》', '《记忆体走私者》', '《天命叛徒观察手册》'],
          commercialCopy:
            '三日倒计时、记忆体篡改、蜂群智能体……这是属于2025年的全新玄幻惊悚爽文。每一章都像在拆盲盒，意外永不停。',
          platformNotes: ['起点：补强人物动机，突出反套路爽点', '番茄：前5章保留密集悬念'],
          emotionBeats: ['震惊 → 惊疑 → 破釜沉舟', '亲情线与末日危机交叉推进'],
          hookDiagnosis: '首章钩子强，建议在3k字内抛出“叛徒即家人”的反转伏笔。',
          characterAlerts: ['主角口癖前后不一致，记得重新对齐语言风格。'],
          foreshadowingReminders: ['第2章提到的“逆脉铭纹”务必在第8章兑现。'],
          endingPitches: [
            '主角化身天幕备份，保留自我意识的同时让世界循环重启。',
            '揭露系统本体即主角未来自我，完成自我博弈闭环。',
          ],
          aiEvasionPlan:
            '章节采用多视角交错、模糊分段标题以及可变字数策略，全书引入原创术语，降低AI检测命中率。',
        }
      : undefined,
    emittedAt: new Date().toISOString(),
  }
}

