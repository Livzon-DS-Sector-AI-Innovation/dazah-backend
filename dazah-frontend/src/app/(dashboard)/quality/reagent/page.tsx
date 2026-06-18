'use client'

import { useState, useCallback, useEffect } from 'react'
import {
  Table,
  Button,
  Space,
  Input,
  Select,
  DatePicker,
  Tag,
  Modal,
  Form,
  InputNumber,
  message,
  Popconfirm,
  Card,
  Row,
  Col,
  Divider,
  Image,
  Upload,
  Tooltip,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  RobotOutlined,
  PictureOutlined,
  DownloadOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import type { UploadFile, RcFile } from 'antd/es/upload'
import {
  Reagent,
  CreateReagentRequest,
  UpdateReagentRequest,
  REAGENT_STATUS_OPTIONS,
  REAGENT_CATEGORY_OPTIONS,
  UNIT_OPTIONS,
} from '@/types/reagent-quality'
import {
  getReagentList,
  getReagentDetail,
  createReagent,
  updateReagent,
  deleteReagent,
  recognizeReagentLabel,
  getNextIncomingLotNo,
  exportReagentsExcel,
} from '@/actions/quality-reagent'

const { Dragger } = Upload

// 试剂名称到编号的映射（包含简称和别名）
const REAGENT_NO_MAP: Record<string, string> = {
  '枸橼酸铋钾': 'A 001',
  '枸橼酸铋（柠檬酸铋）': 'A 002',
  '枸橼酸': 'A 003',
  '氢氧化钾': 'A 005',
  '纯化水': 'A 006',
  '枸橼酸铋钾标签': 'A 007',
  '药用低密度聚乙烯袋': 'A 008',
  '液体无水氨': 'A 009',
  '药用复合袋': 'A 010',
  '纸板包装桶': 'A 011',
  '产品内标签': 'A 012',
  '艾普拉唑': 'B 001',
  '艾普拉唑钠': 'C 001',
  '艾普拉唑中间体APLA': 'B 002',
  '艾普拉唑中间体APLB': 'B 003',
  '艾普拉唑中间体APLC': 'B 004',
  '艾普拉唑中间体APLD': 'B 005',
  '艾普拉唑中间体APLE': 'B 006',
  '4-硝基邻苯二胺': 'B 007',
  '2-氯甲基-3-甲基-4-甲氧基吡啶盐酸盐': 'B 008',
  '2,5-二甲氧基四氢呋喃': 'B 009',
  '氢氧化钾Ⅰ': 'B 010',
  '二硫化碳': 'B 011',
  '冰醋酸': 'B 012',
  '六水合三氯化铁': 'B 013',
  '工业水合肼（80%）': 'B 014',
  '无水醋酸钠': 'B 015',
  '间氯过氧苯甲酸': 'B 016',
  '无水硫酸镁': 'B 017',
  '氢氧化钠': 'B 018',
  '碳酸氢钠': 'B 019',
  '无水亚硫酸钠': 'B 020',
  '三乙胺': 'B 021',
  '无水乙醇': 'B 022',
  '甲醇': 'B 023',
  '二氯甲烷': 'B 024',
  '乙酸乙酯': 'B 025',
  '注射用水': 'B 026',
  '活性炭': 'B 027',
  '硅胶': 'B 028',
  '药用铝瓶': 'B 029',
  '包装泡沫': 'B 030',
  '中性纸箱': 'B 031',
  '低密度聚乙烯袋（黑色）': 'B 032',
  '药用溴化丁基橡胶密封圈': 'B 033',
  '中间产品标签': 'B 034',
  '艾普拉唑标签': 'B 035',
  '纸板包装桶（大）': 'B 036',
  '马来酸氟伏沙明': 'D 001',
  '马来酸氟伏沙粗品': 'D 002',
  '5-甲氧基-1-[4-（三氟甲基）苯基]-1-戊酮（氟伏沙明酮）': 'D 003',
  '马来酸': 'D 004',
  '2-氯乙胺盐酸盐': 'D 005',
  '盐酸羟胺': 'D 006',
  '药用乙醇': 'D 007',
  '乙腈': 'D 008',
  '马来酸氟伏沙明标签': 'D 010',
  '药用低密度聚乙烯袋Ⅰ': 'D 011',
  '盐酸（AR）': 'E 001',
  '吡啶（AR）': 'E 002',
  '醋酐（AR）': 'E 003',
  '溴麝香草酚蓝（AR）': 'E 004',
  '氢氧化钠（AR）': 'E 005',
  '硝酸（AR）': 'E 006',
  '氯化钠（AR）': 'E 007',
  '硝酸银（AR）': 'E 008',
  '硫酸钾（AR）': 'E 009',
  '氯化钡（AR）': 'E 010',
  '比色用氯化钴液': 'E 011',
  '比色用重铬酸钾液': 'E 012',
  '硫酸（AR）': 'E 013',
  '乙醇,95%,500ml/瓶': 'E 014',
  '氯化钙（AR）': 'E 015',
  '卡尔费休氏试剂A液': 'E 016',
  '卡尔费休氏试剂B液，500ml/瓶，5mg/ml': 'E 017',
  '硝酸铅（AR）': 'E 018',
  '醋酸铵（AR）': 'E 019',
  '氨水（AR）': 'E 020',
  '硫代乙酰胺（AR）': 'E 021',
  '甘油（AR）': 'E 022',
  '碘化钾（AR）': 'E 023',
  '氯化亚锡（AR）': 'E 024',
  '国家标准砷溶液': 'E 025',
  '冰醋酸（AR）': 'E 026',
  '结晶紫（AR）': 'E 027',
  '硫脲（AR）': 'E 028',
  '柠檬酸（AR）': 'E 029',
  '硫酸亚铁结晶（AR）': 'E 031',
  '变色硅胶': 'E 032',
  '钠石灰': 'E 033',
  '枸橼酸铵（柠檬酸铵）（AR）': 'E 034',
  '双环酮草酰二腙（AR）': 'E 035',
  '硫酸铜（AR）': 'E 036',
  '氢氧化钾（AR）': 'E 037',
  '二甲酚橙（AR）': 'E 038',
  '铬黑T（AR）': 'E 039',
  '硫氰酸胺（AR）': 'E 040',
  '乙二胺四醋酸二钠（AR）': 'E 041',
  '甲基红（AR）': 'E 042',
  '氯化铵（AR）': 'E 043',
  '溴甲酚绿（AR）': 'E 044',
  '氢氧化钙（AR）': 'E 045',
  '硫酸铁铵（AR）': 'E 046',
  '过硫酸铵（AR）': 'E 047',
  '乙酸铵（AR）': 'E 048',
  '抗坏血酸（AR）': 'E 049',
  '亚铁氰化钾（AR）': 'E 050',
  '磷酸氢二胺（AR）': 'E 051',
  '庚烷磺酸钠（AR）': 'E 052',
  '甲醇（HPLC）': 'E 053',
  '磷酸（AR）': 'E 054',
  '三氯化铁（AR）': 'E 055',
  '酚酞（AR）': 'E 056',
  '高锰酸钾（AR）': 'E 057',
  '乙酸汞（AR）': 'E 058',
  '高氯酸（AR）': 'E 059',
  'pH1.68标准缓冲液': 'E 060',
  'pH4.01标准缓冲液': 'E 061',
  'pH6.86标准缓冲液': 'E 062',
  'pH9.18标准缓冲液': 'E 063',
  'pH=12.45标准缓冲液': 'E 064',
  '草酸铵（AR）': 'E 065',
  '磷酸氢二钠（AR）': 'E 066',
  '酒石酸氢钠（AR）': 'E 067',
  '间苯二酚（AR）': 'E 068',
  '溴（AR）': 'E 069',
  '凡士林（AR）': 'E 070',
  '硫酸肼（AR）': 'E 071',
  '乌洛托品（AR）': 'E 072',
  '中国药典标准比色液': 'E 073',
  '铂-钴标准比色液': 'E 074',
  '甲醇（AR）': 'E 075',
  '乙醇（AR）': 'E 076',
  '丙酮（AR）': 'E 077',
  '二氯甲烷（AR）': 'E 078',
  '乙酸乙酯（AR）': 'E 079',
  '四氢呋喃（AR）': 'E 080',
  '三乙胺（AR）': 'E 081',
  '二乙胺（AR）': 'E 082',
  '一乙胺（AR）': 'E 083',
  '异丙醇（AR）': 'E 084',
  '无水甲醇（AR）': 'E 085',
  '乙醛（AR）': 'E 086',
  '乙缩醛（AR）': 'E 087',
  '苯（AR）': 'E 088',
  '4-甲基－2－戊醇（AR）': 'E 089',
  '正己烷（AR）': 'E 090',
  '乙醚（AR）': 'E 091',
  '三氯甲烷（AR）': 'E 092',
  '异丙醚（AR）': 'E 093',
  '淀粉（AR）': 'E 094',
  '硫代硫酸钠（AR）': 'E 095',
  '无水碳酸钠（AR）': 'E 096',
  '碘（AR）': 'E 097',
  '2,4二硝基苯肼（AR）': 'E 098',
  '硫酸锌（AR）': 'E 099',
  '硫酸奎宁（AR）': 'E 100',
  '碘化汞钾试液': 'E 101',
  '亚甲基蓝（AR）': 'E 102',
  '乙酸钠（AR）': 'E 103',
  '无水乙醇（AR）': 'E 104',
  '正己烷,AR': 'E 105',
  '磷酸氢二铵（AR）': 'E 106',
  '五氧化二磷（AR）': 'E 107',
  '磷酸二氢钾（AR）': 'E 108',
  '乙腈（HPLC）': 'E 109',
  '戊烷磺酸钠': 'E 110',
  '二甲基亚砜（AR）': 'E 111',
  '吐温80': 'E 112',
  '苯甲醛（AR）': 'E 113',
  '次硝酸铋（AR）': 'E 114',
  '硝酸铋（AR）': 'E 115',
  '锌粒': 'E 116',
  '磷酸氢二钾（AR）': 'E 117',
  'N,N-二甲基甲酰胺（AR）': 'E 118',
  '亚硝酸钴钠（AR）': 'E 119',
  '甲基橙（AR）': 'E 120',
  '氯化钾（AR）': 'E 121',
  '碱性碘化汞钾试液': 'E 122',
  '硝酸钾（AR）': 'E 123',
  '二苯胺（AR）': 'E 124',
  '亚硝酸钠（AR）': 'E 125',
  '磺胺（AR）': 'E 126',
  'N-1-奈乙二胺盐酸盐（AR）': 'E 127',
  '酮腙（AR）': 'E 128',
  '比色用硫酸铜溶液': 'E 129',
  '硫酸铵（AR）': 'E 130',
  '正丁醇（AR）': 'E 131',
  '双环己酮二腙（AR）': 'E 132',
  '硼酸（AR）': 'E 133',
  '亚硫酸氢钠（AR）': 'E 134',
  '四氢呋喃（HPLC）': 'E 135',
  '磷酸氢二钾三水合物（AR）': 'E 136',
  '氯化羟胺（AR）': 'E 137',
  '硫氰酸铵（AR）': 'E 138',
  '碳酸氢钠（AR）': 'E 139',
  '磷酸氢二钠结晶（AR）': 'E 140',
  '氢氟酸（AR）': 'E 141',
  '乙酸酐（AR）': 'E 142',
  '无水硫酸钠（AR）': 'E 143',
  '六次甲基四胺（AR）': 'E 144',
  '重铬酸钾（PT）': 'E 145',
  '四丁基溴化铵': 'E 146',
  '无水磷酸氢二钾': 'E 147',
  '六水合氯化镁': 'E 148',
  '亚磷酸三乙酯': 'E 149',
  '枸橼酸钠': 'E 150',
  '四庚基溴化铵': 'E 151',
  '铝试剂（AR）': 'E 153',
  '阿拉伯树胶粉（AR）': 'E 154',
  '二水合草酸(草酸)（AR）': 'E 155',
  '盐酸苯肼（AR）': 'E 156',
  '四水合钼酸铵(钼酸铵)（AR）': 'E 157',
  '溴化钾（SP）': 'E 158',
  '铁氰化钾（AR）': 'E 159',
  '十二水合硫酸铝钾(硫酸铝钾)（AR）': 'E 160',
  '盐酸标准溶液（0.1mol/L）': 'E 161',
  '磷酸（GR）': 'E 162',
  '三氟乙酸（AR）': 'E 163',
  '醋酸铅棉花（AR）': 'E 164',
  '乙腈（AR）': 'E 165',
  '乙二胺四乙酸二钠盐，二水（AR）': 'E 166',
  '邻氨基酚（AR）': 'E 167',
  '镁（SSS）': 'E 168',
  '钠（SSS）': 'E 169',
  '钙（SSS）': 'E 170',
  '铜（SSS）': 'E 171',
  '钾（SSS）': 'E 172',
  '铋（SSS）': 'E 173',
  '银（SSS）': 'E 174',
  '铁（SSS）': 'E 175',
  '2-甲基四氢呋喃（GC）': 'E 176',
  '正庚烷（AR）': 'E 177',
  '乙酸丁酯（AR）': 'E 178',
  '玉米糊精（AR）': 'E 179',
  '二甲基黄（IND）': 'E 180',
  '定氮合金（AR）': 'E 181',
  '三氟乙酸（HPLC）': 'E 182',
  '荧光素（AR）': 'E 183',
  '十水合四硼酸钠（AR）': 'E 184',
  '甲基叔丁基醚（AR）': 'E 185',
  '二甲苯（AR）': 'E 186',
  '氯化钠（PT）': 'E 187',
  '4-甲氧基-1-丁醇（AR）': 'E 188',
  '硫化铁（AR）': 'E 189',
  '1，10-菲啰啉（AR）': 'E 190',
  '碳酸钙（AR）': 'E 191',
  '邻苯二甲酸氢钾（PT）': 'E 192',
  '无水碳酸钠（PT）': 'E 193',
  '草酸钠（PT）': 'E 194',
  '氧化锌（PT）': 'E 195',
  '溴化汞试纸': 'E 196',
  '红石蕊试纸': 'E 197',
  'pH检测试纸': 'E 198',
  '碘化钠（AR）': 'E 199',
  '氧化钬（AR）': 'E 200',
  '2.6-二叔丁基对甲酚（GC）': 'E 201',
  '三乙醇胺（AR）': 'E 202',
  'L（+）-酒石酸（AR）': 'E 203',
  '异丙醇（HPLC）': 'E 204',
  '磷酸二氢铵（HPLC）': 'E 205',
  '甲苯（AR）': 'E 206',
  '丙酮（HPLC）': 'E 207',
  '正已烷（HPLC）': 'E 208',
  'GS3异构体/MSTB异构体对照品': 'E 209',
  '5-羟基-4-甲氧基-2，3-二甲基吡啶对照品': 'E 210',
  '杂质RR0.96对照品': 'E 211',
  '索玛四肽RRT1.03对照品': 'E 212',
  '甘氨酸乙酯盐酸盐对照品': 'E 213',
  'N-苄氧羰基-D-谷氨酸5-叔丁酯异构体对照品': 'E 214',
  'N-Boc-N\'-三苯甲基-D-组氨酸异构体对照品': 'E 215',
  'N-苄氧羰基-L-谷氨酸5-叔丁酯对照品': 'E 216',
  'N-Boc-N\'-三苯甲基-L-组氨酸对照品': 'E 217',
  '2-甲基丙氨酸甲酯盐酸盐对照品': 'E 218',
  'AEEA-AEEA-AEEA对照品': 'E 219',
  '1-羟基苯并噻唑对照品': 'E 220',
  'β-Ala-2A对照品': 'E 221',
  'AEEA-AEEA对照品': 'E 222',
  'β-Ala-AEEA对照品': 'E 223',
  'MSTA对照品': 'E 224',
  '2,2,2-三氟乙胺盐酸盐/弗雷拉纳杂质C对照品': 'E 225',
  '四肽RRTO.84对照品': 'E 226',
  'MSTB对照品': 'E 227',
  'MSTC对照品': 'E 228',
  'MSTC异构体对照品': 'E 229',
  'MSTE对照品': 'E 230',
  '三肽对照品': 'E 231',
  '四肽乙酯（杂质E）对照品': 'E 232',
  'N,N-二甲基对苯二胺盐酸盐（CP）对照品': 'E 233',
  '二甲基亚砜': 'E 234',
  '余氯试纸': 'E 235',
  '顺丁烯二酸酐（AR）': 'E 236',
  '乙醛': 'E 237',
  '对三氟甲基苯腈': 'E 238',
  '奈斯勒试剂': 'E 239',
  '2-甲基四氢呋喃': 'E 240',
  '3AEEA衍生物对照品': 'E 241',
  '单AEEA衍生物对照品': 'E 243',
  '1,4-丁二醇单甲醚': 'E 244',
  '索玛鲁肽侧链主成分对照品': 'E 245',
  '侧链异构体对照品': 'E 246',
  '氟雷拉纳': 'E 247',
  '氟雷拉纳S异构体': 'E 248',
  '2-氯甲基-3-甲基-4-甲氧基吡啶盐酸盐对照品': 'E 249',
  '四肽（四肽主成分）对照品': 'E 250',
  '异丙醇(HPLC)': 'E 251',
  '五肽（杂质D)对照品': 'E 252',
  '非对应异构体（四肽杂质F)对照品': 'E 253',
  '2，5二甲氧基四氢呋喃对照品': 'E 254',
  'AEEA对照品': 'E 255',
  'Trt-OH(四肽杂质B)对照品': 'E 257',
  '二硫化二苯并噻唑对照品': 'E 258',
  '5-氨基-2-巯基苯井咪唑对照品': 'E 259',
  '1-乙基-(3-二甲基氨基丙基)碳二亚胺盐酸盐对照品': 'E 260',
  '4-甲氧基-1-丁醇': 'E 261',
  '磷酸（HPLC）': 'E 262',
  '无水柠檬酸': 'E 263',
  '丁二酸二辛酯磺酸钠': 'E 264',
  '2-氯甲基-3-甲基-4-甲氧基吡啶对照品': 'E 265',
  '百里香酚酞': 'E 267',
  '2-巯基-5-硝基苯井咪唑对照品': 'E 268',
  '4-甲氧基-3-甲基-2-吡啶甲醇对照品': 'E 269',
  '二氧化锰': 'E 270',
  '正丙醇（AR）': 'E 271',
  '乙醇胺(ACS)': 'E 272',
  '二氯甲烷（HPLC）': 'E 273',
  '(S)-5-(叔丁氧基)-2-(2-((S)-2-((叔丁氧羰基)氨基)-3-(1-三苯甲基-1H-咪唑-4基)丙酰胺基）-2-甲基丙酰胺对照品': 'E 274',
  '硫化钠-丙三醇溶液': 'E 275',
  '石油醚(标准溶液)': 'E 276',
  '水中磷酸盐': 'E 277',
  '二甲苯': 'E 278',
  '氟雷拉纳中间体九对照品': 'E 279',
  '2-氨基异丁酸对照品': 'E 280',
  '十八烷二酸单叔丁酯': 'E 281',
  'AE活性酯对照品': 'E 282',
  '氨噻肟酸对照品': 'E 283',
  '反式乌头酸对照品': 'E 284',
  '顺式-乌头酸对照品': 'E 285',
  '硝酸钾': 'E 286',
  '1-氯-4-甲氧基丁烷': 'E 287',
  '2-巯基-5-吡咯基苯并咪唑': 'E 288',
  '氟伏沙明酮对照品': 'E 289',
  '硫': 'E 290',
  '2-巯基苯并噻唑对照品': 'E 291',
  'FL-01': 'E 292',
  'FL-01A': 'E 293',
  'FL-01D': 'E 294',
  'FL-01F': 'E 295',
  'FL-02A': 'E 296',
  'FL-01B': 'E 297',
  'FL-02C': 'E 298',
  'FL-02D': 'E 299',
  'FL-02E': 'E 300',
  'FL-02': 'E 301',
  '3-羟基-4-碘苯甲酸（LS-SMA-1)': 'E 302',
  '硝酸钠': 'E 303',
  '三甲胺溶液': 'E 304',
  '3-羟基-4-（（三甲基硅烷基）乙炔基）苯甲酸（LS-SMA-2）': 'E 305',
  '苯并呋喃-6-甲酸甲酯（LS-SMA-3）': 'E 306',
  '苯并呋喃-6-羧酸（LS-SMA）': 'E 307',
  '艾普拉唑氮氧化物（LZ1001-IN5-IM2）': 'E 308',
  '艾普拉唑杂质2（LZ1001-IMC）': 'E 309',
  '艾普拉唑磺酰化物': 'E 310',
  '艾普拉唑硫醚': 'E 311',
  '糖精': 'E 313',
  '非那西丁': 'E 314',
  '乙酰苯胺': 'E 315',
  '香草醛': 'E 316',
  '酚酞': 'E 317',
  '磺胺二甲嘧啶': 'E 318',
  '1，4-对苯醌': 'E 319',
  '蔗糖': 'E 320',
  '盐酸二甲胺': 'E 321',
  '4-乙酰基-2-甲基苯甲酸': 'E 322',
  'LS-SMB-1': 'E 323',
  'LS-SMB-3': 'E 324',
  'LS-SMC-2': 'E 325',
  'LS-SMC-1': 'E 326',
  '标准水溶液': 'E 327',
  '聚合物悬浮液浊度标准溶液': 'E 328',
  '邻苯二甲酸氢钾（KHP)标准液': 'E 329',
  'N,N-二乙丙基乙胺': 'E 330',
  '二环己胺': 'E 331',
  '脯氨酸/（L-脯氨酸）': 'E 332',
  'N-[(1r，4r)-4-(氯甲基)环己基]-N-甲基-7-甲苯磺酰基-7H-吡咯并[2，3-d]嘧啶-4-胺': 'E 333',
  '(1r，4r)-4-(甲基(7H-吡咯并[2，3-d]嘧啶-4-基)氨基)环己基)甲醇': 'E 334',
  '马来酸奥拉替尼杂质13/7H-吡咯并[2，3-d]嘧啶-4-醇': 'E 335',
  '4-氯-7H-吡咯并[2，3-d]嘧啶': 'E 336',
  '((1r，4r)-4-(甲基(7-甲苯磺酰基-7H-吡咯并[2，3-d]嘧啶-4-基)氨基)环己基)甲基 4-甲基苯磺酸酯': 'E 337',
  '艾普拉唑杂质21/LZ1001-IMA': 'E 338',
  'LS-SMB-12': 'E 340',
  'N-甲基吡咯烷酮': 'E 341',
  'LS-SMB': 'E 342',
  'LS-SMC': 'E 343',
  '立他司特': 'E 344',
  'LS-IN1': 'E 345',
  'LS-IN2': 'E 346',
  'LS-IN3': 'E 347',
  'LS-IM3': 'E 348',
  '对甲苯磺酸4-甲基苯磺酸一水合物': 'E 349',
  'L-苏氨酸': 'E 350',
  '水合茚三铜': 'E 351',
  '蓝石蕊试纸': 'E 352',
  '醋酸铅试纸': 'E 353',
  'LS-IN3-5': 'E 354',
  'LS-IN3-4': 'E 355',
  'LS-IN2-4': 'E 356',
  'LS-IN2-5': 'E 357',
  '甲酸': 'E 358',
  '六水合氯化钴': 'E 359',
  'LS-SMC-8': 'E 360',
  'LS-SMC-11': 'E 361',
  'LS-IN3-7': 'E 362',
  'LS-IN3-6': 'E 363',
  'LS-IN2-1': 'E 364',
  'LS-SMB-2': 'E 365',
  '溴试液': 'E 366',
  '无水甲酸': 'E 367',
  'LS-IN3-1': 'E 368',
  'LS-IN3-8': 'E 369',
  'FL-3G': 'E 370',
  'FL-3I': 'E 371',
  'FL-2': 'E 372',
  'FL-3F': 'E 373',
  'FL-1': 'E 374',
  '甲醛溶液': 'E 375',
  '铬酸钾': 'E 376',
  '氟雷拉纳R异构体': 'E 378',
  'LS-SMC-5': 'E 379',
  '4-二甲氨基吡啶': 'E 380',
  '高氯酸钬溶液': 'E 381',
  'N-甲基吡咯烷酮(NMP)': 'E 382',
  '立他司特中间体LTSC': 'E 383',
  '氟雷拉纳杂质FL-3G': 'E 384',
  '氟雷拉纳杂质FL-31': 'E 385',
  '七氟丁酸': 'E 386',
  '氯化钾电导率溶液标准物质': 'E 387',
  '氟雷拉纳甘铵盐对照品': 'E 388',
  '氟雷拉纳杂质E': 'E 389',
  '氟雷拉纳杂质FL-3F': 'E 390',
  '甘氨酸': 'E 391',
  '4-（3-（3，5-二氯苯基）-4，4，4-三氟丁烯酰基）-2-甲基苯甲酸': 'E 392',
  '4-（3-（3，5-二氯苯基）-4，4，4-三氟-3-羟基丁酰基）-2-甲基苯甲酸': 'E 393',
  '甘露醇（分析纯）': 'E 394',
  '氯化钾（光谱纯SP）': 'E 395',
  '无水乙酸钠': 'E 396',
  '1-溴-3，5-二氯苯': 'E 397',
  '1-溴-2，6-二氯苯': 'E 398',
  '2，4-二氯溴苯': 'E 399',
  '3\',5\'-二氯-2，2，2-三氟乙酰苯酮': 'E 400',
  '1，2，3，4-四氢异喹啉-6-羧酸': 'E 401',
  '2-(苯并呋喃-6-羰基)-5-氯-1，2，3，4-四氢异喹啉-6-羧酸': 'E 402',
  '(S)-2-(2-(苯并呋喃-6-羰基)-5-氯-1，2，3，4-四氢异喹啉-6-羧酸胺)-3-(3-(甲磺酰基)苯基)丙酸': 'E 403',
  '7-氯-1，2，3，4-四氢异喹啉-6-羧酸盐酸盐': 'E 404',
  '5-氯-1，2，3，4-四氢异喹啉-6-羧酸盐酸盐': 'E 405',
  '(S)-2-(2-(苯并呋喃-6-羰基)-7-氯-1，2，3，4-四氢异喹啉-6-羧酸胺)-3-(3-(甲磺酰基)苯基)丙酸': 'E 406',
  '2-(苯并呋喃-6-羰基)-7-氯-1,2,3,4-四氢异喹啉-6-羧酸': 'E 407',
}

// 根据试剂名称查找编号（支持模糊匹配）
function findReagentNo(name: string): string | undefined {
  if (!name) return undefined

  // 1. 精确匹配
  if (REAGENT_NO_MAP[name]) {
    return REAGENT_NO_MAP[name]
  }

  // 2. 去除所有空格后匹配
  const normalizedName = name.replace(/\s+/g, '')
  for (const key in REAGENT_NO_MAP) {
    if (key.replace(/\s+/g, '') === normalizedName) {
      return REAGENT_NO_MAP[key]
    }
  }

  // 3. 去除括号内容后匹配（如 "氢氧化钠（AR）" -> "氢氧化钠"）
  const noParens = name.replace(/\([^)]*\)/g, '').replace(/\s+/g, '').trim()
  for (const key in REAGENT_NO_MAP) {
    const keyNoParens = key.replace(/\([^)]*\)/g, '').replace(/\s+/g, '').trim()
    if (keyNoParens === noParens) {
      return REAGENT_NO_MAP[key]
    }
  }

  // 4. 部分匹配（AI返回的名称可能包含一些额外字符）
  for (const key in REAGENT_NO_MAP) {
    if (name.includes(key) || key.includes(name)) {
      return REAGENT_NO_MAP[key]
    }
  }

  // 5. 关键词提取匹配（提取核心关键词）
  const keywords = name.replace(/[（），。,\s\/\(\)]/g, '').trim()
  if (keywords.length >= 2) {
    for (const key in REAGENT_NO_MAP) {
      const keyClean = key.replace(/[（），。,\s\/\(\)]/g, '')
      // 检查关键词是否在映射表键中，或映射表键是否在关键词中
      if (keyClean.includes(keywords) || keywords.includes(keyClean)) {
        return REAGENT_NO_MAP[key]
      }
    }
  }

  return undefined
}

// 状态颜色映射
const STATUS_COLORS: Record<string, string> = {
  available: 'green',
  low_stock: 'orange',
  expired: 'red',
  quarantine: 'blue',
  scrap: 'gray',
}

// 初始筛选条件
const initialFilters = {
  keyword: '',
  category: undefined as string | undefined,
  status: undefined as string | undefined,
}

export default function QualityReagentPage() {
  // 状态
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<Reagent[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [filters, setFilters] = useState(initialFilters)

  // 表单实例
  const [createForm] = Form.useForm()
  const [editForm] = Form.useForm()

  // 弹窗状态
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [editRecord, setEditRecord] = useState<Reagent | null>(null)
  const [viewRecord, setViewRecord] = useState<Reagent | null>(null)
  const [viewModalVisible, setViewModalVisible] = useState(false)

  // 图片上传状态
  const [createFileList, setCreateFileList] = useState<UploadFile[]>([])
  const [editFileList, setEditFileList] = useState<UploadFile[]>([])
  const [uploadedUrls, setUploadedUrls] = useState<string[]>([])

  // AI识别状态
  const [aiLoading, setAiLoading] = useState(false)
  const [submitLoading, setSubmitLoading] = useState(false)

  // 加载数据
  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const response = await getReagentList({
        keyword: filters.keyword || undefined,
        category: filters.category,
        status: filters.status,
        page,
        page_size: pageSize,
      })

      if (response.code === 200) {
        setData(response.data.items || [])
        setTotal(response.data.total || 0)
      } else {
        message.error(response.message || '加载失败')
      }
    } catch (error) {
      message.error('加载数据失败')
    } finally {
      setLoading(false)
    }
  }, [filters, page, pageSize])

  useEffect(() => {
    loadData()
  }, [loadData])

  // 筛选
  const handleSearch = () => {
    setPage(1)
    loadData()
  }

  // 重置筛选
  const handleReset = () => {
    setFilters(initialFilters)
    setPage(1)
    loadData()
  }

  // 导出Excel
  const handleExport = async () => {
    try {
      message.loading('正在导出...')
      await exportReagentsExcel({
        keyword: filters.keyword || undefined,
        category: filters.category,
        status: filters.status,
      })
      message.success('导出成功')
    } catch (error) {
      message.error('导出失败')
    }
  }

  // 新建
  const handleCreate = async () => {
    createForm.resetFields()
    
    // 获取下一个入场批号
    let incomingLotNo = ''
    try {
      const response = await getNextIncomingLotNo()
      if (response.code === 200 && response.data) {
        incomingLotNo = response.data.incoming_lot_no
      }
    } catch (e) {
      console.error('获取入场批号失败:', e)
    }
    
    createForm.setFieldsValue({
      arrival_date: dayjs(),
      category: '/',
      quantity: 0,
      unit: 'g',
      incoming_lot_no: incomingLotNo,
    })
    setCreateFileList([])
    setUploadedUrls([])
    setCreateModalVisible(true)
  }

  // 编辑
  const handleEdit = async (record: Reagent) => {
    try {
      const response = await getReagentDetail(record.id)
      if (response.code === 200 && response.data) {
        setEditRecord(response.data)
        editForm.setFieldsValue({
          ...response.data,
          arrival_date: response.data.arrival_date ? dayjs(response.data.arrival_date) : null,
          production_date: response.data.production_date ? dayjs(response.data.production_date) : null,
          expiration_date: response.data.expiration_date ? dayjs(response.data.expiration_date) : null,
        })
        // 设置已有图片
        const existingFiles = (response.data.reagent_label_urls || []).map((url, index) => ({
          uid: String(-index - 1),
          name: `image-${index}`,
          status: 'done' as const,
          url: url,
        }))
        setEditFileList(existingFiles)
        setUploadedUrls(response.data.reagent_label_urls || [])
        setEditModalVisible(true)
      } else {
        message.error(response.message || '获取数据失败')
      }
    } catch (error) {
      message.error('获取数据失败')
    }
  }

  // 查看详情
  const handleView = async (record: Reagent) => {
    try {
      const response = await getReagentDetail(record.id)
      if (response.code === 200 && response.data) {
        setViewRecord(response.data)
        setViewModalVisible(true)
      } else {
        message.error(response.message || '获取数据失败')
      }
    } catch (error) {
      message.error('获取数据失败')
    }
  }

  // 删除
  const handleDelete = async (id: string) => {
    try {
      const response = await deleteReagent(id)
      if (response.code === 200) {
        message.success('删除成功')
        loadData()
      } else {
        message.error(response.message || '删除失败')
      }
    } catch (error) {
      message.error('删除失败')
    }
  }

  // AI识别
  const handleAiRecognize = async (form: 'create' | 'edit') => {
    const fileList = form === 'create' ? createFileList : editFileList
    const files = fileList
      .filter((f) => f.originFileObj)
      .map((f) => f.originFileObj as RcFile)

    if (files.length === 0) {
      message.warning('请先上传至少一张试剂标签图片')
      return
    }

    setAiLoading(true)
    try {
      const response = await recognizeReagentLabel(files)
      if (response.code === 200 && response.data) {
        const formInstance = form === 'create' ? createForm : editForm
        const data = response.data

        // 自动填充表单
        console.log('AI识别返回数据:', JSON.stringify(data, null, 2))
        
        if (data.reagent_name) {
          formInstance.setFieldValue('reagent_name', data.reagent_name)
          // 根据试剂名称自动填入编号（使用模糊匹配）
          const reagentNo = findReagentNo(data.reagent_name)
          console.log('试剂名称:', data.reagent_name, '-> 找到编号:', reagentNo)
          if (reagentNo) {
            formInstance.setFieldValue('reagent_no', reagentNo)
          }
        }
        if (data.lot_no) formInstance.setFieldValue('lot_no', data.lot_no)
        if (data.manufacturer) formInstance.setFieldValue('manufacturer', data.manufacturer)
        if (data.content) formInstance.setFieldValue('content', data.content)

        // 处理生产日期和有效期
        if (data.production_date) {
          formInstance.setFieldValue('production_date', dayjs(data.production_date))
          // 如果没有有效期但有生产日期，计算有效期=生产日期+3年
          if (data.expiration_date) {
            formInstance.setFieldValue('expiration_date', dayjs(data.expiration_date))
          } else {
            const expirationDate = dayjs(data.production_date).add(3, 'year')
            formInstance.setFieldValue('expiration_date', expirationDate)
          }
        } else if (data.expiration_date) {
          // 有有效期但没有生产日期
          formInstance.setFieldValue('expiration_date', dayjs(data.expiration_date))
        }

        // 处理规格（含单位，如 500g、250ml、1L）
        if (data.specification) {
          formInstance.setFieldValue('specification', data.specification)
          // 尝试从规格中提取单位和数值
          const specMatch = data.specification.match(/^(\d+(?:\.\d+)?)\s*(g|kg|ml|l|litre|liter|mg)$/i)
          if (specMatch) {
            const value = parseFloat(specMatch[1])
            const unitLower = specMatch[2].toLowerCase()
            // 根据单位设置数量和单位
            formInstance.setFieldValue('quantity', value)
            // 映射单位
            const unitMap: Record<string, string> = {
              'g': 'g', 'kg': 'kg', 'mg': 'mg',
              'ml': 'ml', 'l': 'L', 'litre': 'L', 'liter': 'L'
            }
            const mappedUnit = unitMap[unitLower] || unitLower.toUpperCase()
            formInstance.setFieldValue('unit', mappedUnit)
          }
        }

        message.success(`AI识别完成，置信度: ${(data.confidence * 100).toFixed(0)}%`)
      } else {
        message.error(response.message || 'AI识别失败')
      }
    } catch (error) {
      message.error('AI识别失败，请重试')
    } finally {
      setAiLoading(false)
    }
  }

  // 提交新建表单
  const handleCreateSubmit = async () => {
    try {
      const values = await createForm.validateFields()

      const submitData: CreateReagentRequest = {
        reagent_label_urls: uploadedUrls,
        reagent_name: values.reagent_name,
        arrival_date: values.arrival_date.format('YYYY-MM-DD'),
        production_date: values.production_date?.format('YYYY-MM-DD'),
        lot_no: values.lot_no,
        incoming_lot_no: values.incoming_lot_no,
        expiration_date: values.expiration_date.format('YYYY-MM-DD'),
        specification: values.specification,
        category: values.category,
        reagent_no: values.reagent_no,
        content: values.content,
        manufacturer: values.manufacturer,
        quantity: values.quantity,
        unit: values.unit,
      }

      setSubmitLoading(true)
      const response = await createReagent(submitData)

      if (response.code === 200) {
        message.success('创建成功')
        setCreateModalVisible(false)
        loadData()
      } else {
        message.error(response.message || '创建失败')
      }
    } catch (error: unknown) {
      if ((error as { errorFields?: unknown }).errorFields) {
        return
      }
      message.error((error as Error).message || '操作失败')
    } finally {
      setSubmitLoading(false)
    }
  }

  // 提交编辑表单
  const handleEditSubmit = async () => {
    try {
      const values = await editForm.validateFields()

      const submitData: UpdateReagentRequest = {
        reagent_label_urls: uploadedUrls,
        reagent_name: values.reagent_name,
        arrival_date: values.arrival_date?.format('YYYY-MM-DD'),
        production_date: values.production_date?.format('YYYY-MM-DD'),
        lot_no: values.lot_no,
        incoming_lot_no: values.incoming_lot_no,
        expiration_date: values.expiration_date?.format('YYYY-MM-DD'),
        specification: values.specification,
        category: values.category,
        reagent_no: values.reagent_no,
        content: values.content,
        manufacturer: values.manufacturer,
        quantity: values.quantity,
        unit: values.unit,
        status: values.status,
      }

      setSubmitLoading(true)
      const response = await updateReagent(editRecord!.id, submitData)

      if (response.code === 200) {
        message.success('更新成功')
        setEditModalVisible(false)
        loadData()
      } else {
        message.error(response.message || '更新失败')
      }
    } catch (error: unknown) {
      if ((error as { errorFields?: unknown }).errorFields) {
        return
      }
      message.error((error as Error).message || '操作失败')
    } finally {
      setSubmitLoading(false)
    }
  }

  // 处理新建图片上传变化
  const handleCreateFileChange = ({ fileList: newFileList }: { fileList: UploadFile[] }) => {
    setCreateFileList(newFileList)
  }

  // 处理编辑图片上传变化
  const handleEditFileChange = ({ fileList: newFileList }: { fileList: UploadFile[] }) => {
    setEditFileList(newFileList)
  }

  // 图片上传预览
  const handlePreview = async (file: UploadFile) => {
    let url = file.url
    if (!url && file.originFileObj) {
      url = URL.createObjectURL(file.originFileObj)
    }
    if (url) {
      window.open(url, '_blank')
    }
  }

  // 表格列定义
  const columns: ColumnsType<Reagent> = [
    {
      title: '试剂标签',
      dataIndex: 'reagent_label_urls',
      key: 'reagent_label_urls',
      width: 100,
      render: (urls: string[] | null) => {
        if (!urls || urls.length === 0) return '-'
        return (
          <Image.PreviewGroup items={urls}>
            <Image
              src={urls[0]}
              width={60}
              height={60}
              style={{ objectFit: 'cover' }}
              placeholder={<PictureOutlined style={{ fontSize: 24 }} />}
            />
          </Image.PreviewGroup>
        )
      },
    },
    {
      title: '试剂名称',
      dataIndex: 'reagent_name',
      key: 'reagent_name',
      width: 150,
      ellipsis: true,
    },
    {
      title: '到货日期',
      dataIndex: 'arrival_date',
      key: 'arrival_date',
      width: 110,
      render: (value) => value ? dayjs(value).format('YYYY-MM-DD') : '-',
    },
    {
      title: '生产日期',
      dataIndex: 'production_date',
      key: 'production_date',
      width: 110,
      render: (value) => value ? dayjs(value).format('YYYY-MM-DD') : '-',
    },
    {
      title: '批号',
      dataIndex: 'lot_no',
      key: 'lot_no',
      width: 120,
    },
    {
      title: '入场批号',
      dataIndex: 'incoming_lot_no',
      key: 'incoming_lot_no',
      width: 120,
    },
    {
      title: '有效期',
      dataIndex: 'expiration_date',
      key: 'expiration_date',
      width: 110,
      render: (value) => value ? dayjs(value).format('YYYY-MM-DD') : '-',
    },
    {
      title: '规格',
      dataIndex: 'specification',
      key: 'specification',
      width: 100,
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 80,
      render: (value) => {
        const option = REAGENT_CATEGORY_OPTIONS.find((o) => o.value === value)
        return option?.label || value
      },
    },
    {
      title: '编号',
      dataIndex: 'reagent_no',
      key: 'reagent_no',
      width: 100,
    },
    {
      title: '含量',
      dataIndex: 'content',
      key: 'content',
      width: 80,
    },
    {
      title: '生产厂家',
      dataIndex: 'manufacturer',
      key: 'manufacturer',
      width: 150,
      ellipsis: true,
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 80,
      render: (value, record) => `${value} ${record.unit}`,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 90,
      render: (value) => (
        <Tag color={STATUS_COLORS[value] || 'default'}>
          {REAGENT_STATUS_OPTIONS.find((o) => o.value === value)?.label || value}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button type="link" size="small" onClick={() => handleView(record)}>
            查看
          </Button>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Popconfirm
            title="确定删除？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div style={{ padding: 24 }}>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={6}>
              <Input
                placeholder="关键词搜索"
                value={filters.keyword}
                onChange={(e) => setFilters({ ...filters, keyword: e.target.value })}
                allowClear
              />
            </Col>
            <Col span={4}>
              <Select
                placeholder="分类"
                value={filters.category}
                onChange={(value) => setFilters({ ...filters, category: value })}
                allowClear
                style={{ width: '100%' }}
              >
                {REAGENT_CATEGORY_OPTIONS.map((option) => (
                  <Select.Option key={option.value} value={option.value}>
                    {option.label}
                  </Select.Option>
                ))}
              </Select>
            </Col>
            <Col span={4}>
              <Select
                placeholder="状态"
                value={filters.status}
                onChange={(value) => setFilters({ ...filters, status: value })}
                allowClear
                style={{ width: '100%' }}
              >
                {REAGENT_STATUS_OPTIONS.map((option) => (
                  <Select.Option key={option.value} value={option.value}>
                    {option.label}
                  </Select.Option>
                ))}
              </Select>
            </Col>
            <Col span={10} style={{ textAlign: 'right' }}>
              <Space>
                <Button type="primary" onClick={handleSearch}>查询</Button>
                <Button onClick={handleReset}>重置</Button>
                <Button icon={<DownloadOutlined />} onClick={handleExport}>
                  导出Excel
                </Button>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                  新建试剂
                </Button>
              </Space>
            </Col>
          </Row>
        </div>

        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1800 }}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (p, ps) => {
              setPage(p)
              setPageSize(ps)
            },
          }}
        />
      </Card>

      {/* 新建弹窗 */}
      <Modal
        title="新建试剂/标准品"
        open={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        width={900}
        destroyOnHidden
        footer={
          <Space>
            <Button onClick={() => setCreateModalVisible(false)}>取消</Button>
            <Button type="primary" onClick={handleCreateSubmit} loading={submitLoading}>
              创建
            </Button>
          </Space>
        }
      >
        <Form form={createForm} layout="vertical">
          <Divider>试剂标签图片</Divider>
          <Row gutter={16}>
            <Col span={16}>
              <Dragger
                fileList={createFileList}
                onChange={handleCreateFileChange}
                beforeUpload={() => false}
                multiple
                maxCount={5}
                onPreview={handlePreview}
                listType="picture-card"
              >
                <p className="ant-upload-drag-icon">
                  <PictureOutlined />
                </p>
                <p className="ant-upload-text">点击或拖拽上传试剂标签图片</p>
                <p className="ant-upload-hint">支持多张图片上传，AI将识别图片中的试剂信息</p>
              </Dragger>
            </Col>
            <Col span={8} style={{ display: 'flex', alignItems: 'center' }}>
              <Button
                type="primary"
                icon={<RobotOutlined />}
                loading={aiLoading}
                onClick={() => handleAiRecognize('create')}
                disabled={createFileList.length === 0}
              >
                AI识别标签
              </Button>
            </Col>
          </Row>

          <Divider>基本信息</Divider>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="reagent_name" label="试剂名称" rules={[{ required: true }]}>
                <Input placeholder="请输入试剂名称" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="lot_no" label="批号" rules={[{ required: true }]}>
                <Input placeholder="请输入批号" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="category" label="分类" rules={[{ required: true }]}>
                <Select placeholder="请选择分类">
                  {REAGENT_CATEGORY_OPTIONS.map((option) => (
                    <Select.Option key={option.value} value={option.value}>
                      {option.label}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="specification" label="规格">
                <Input placeholder="请输入规格" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="manufacturer" label="生产厂家">
                <Input placeholder="请输入生产厂家" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="content" label="含量">
                <Input placeholder="如：98%、AR级等" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="arrival_date" label="到货日期" rules={[{ required: true }]}>
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="production_date" label="生产日期">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="expiration_date" label="有效期" rules={[{ required: true }]}>
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="reagent_no" label="编号">
                <Input placeholder="试剂编号" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="incoming_lot_no" label="入场批号">
                <Input placeholder="入场批号" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="quantity" label="数量" rules={[{ required: true }]}>
                <InputNumber style={{ width: '100%' }} min={0} placeholder="数量" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="unit" label="单位" rules={[{ required: true }]}>
                <Select placeholder="请选择单位">
                  {UNIT_OPTIONS.map((option) => (
                    <Select.Option key={option.value} value={option.value}>
                      {option.label}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* 编辑弹窗 */}
      <Modal
        title="编辑试剂/标准品"
        open={editModalVisible}
        onCancel={() => setEditModalVisible(false)}
        width={900}
        destroyOnHidden
        footer={
          <Space>
            <Button onClick={() => setEditModalVisible(false)}>取消</Button>
            <Button type="primary" onClick={handleEditSubmit} loading={submitLoading}>
              保存
            </Button>
          </Space>
        }
      >
        <Form form={editForm} layout="vertical">
          <Divider>试剂标签图片</Divider>
          <Row gutter={16}>
            <Col span={16}>
              <Dragger
                fileList={editFileList}
                onChange={handleEditFileChange}
                beforeUpload={() => false}
                multiple
                maxCount={5}
                onPreview={handlePreview}
                listType="picture-card"
              >
                <p className="ant-upload-drag-icon">
                  <PictureOutlined />
                </p>
                <p className="ant-upload-text">点击或拖拽上传试剂标签图片</p>
                <p className="ant-upload-hint">支持多张图片上传，AI将识别图片中的试剂信息</p>
              </Dragger>
            </Col>
            <Col span={8} style={{ display: 'flex', alignItems: 'center' }}>
              <Button
                type="primary"
                icon={<RobotOutlined />}
                loading={aiLoading}
                onClick={() => handleAiRecognize('edit')}
                disabled={editFileList.length === 0}
              >
                AI识别标签
              </Button>
            </Col>
          </Row>

          <Divider>基本信息</Divider>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="reagent_name" label="试剂名称" rules={[{ required: true }]}>
                <Input placeholder="请输入试剂名称" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="lot_no" label="批号" rules={[{ required: true }]}>
                <Input placeholder="请输入批号" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="category" label="分类" rules={[{ required: true }]}>
                <Select placeholder="请选择分类">
                  {REAGENT_CATEGORY_OPTIONS.map((option) => (
                    <Select.Option key={option.value} value={option.value}>
                      {option.label}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="specification" label="规格">
                <Input placeholder="请输入规格" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="manufacturer" label="生产厂家">
                <Input placeholder="请输入生产厂家" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="content" label="含量">
                <Input placeholder="如：98%、AR级等" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="arrival_date" label="到货日期" rules={[{ required: true }]}>
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="production_date" label="生产日期">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="expiration_date" label="有效期" rules={[{ required: true }]}>
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="reagent_no" label="编号">
                <Input placeholder="试剂编号" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="incoming_lot_no" label="入场批号">
                <Input placeholder="入场批号" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="quantity" label="数量" rules={[{ required: true }]}>
                <InputNumber style={{ width: '100%' }} min={0} placeholder="数量" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="unit" label="单位" rules={[{ required: true }]}>
                <Select placeholder="请选择单位">
                  {UNIT_OPTIONS.map((option) => (
                    <Select.Option key={option.value} value={option.value}>
                      {option.label}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="status" label="状态">
                <Select placeholder="请选择状态">
                  {REAGENT_STATUS_OPTIONS.map((option) => (
                    <Select.Option key={option.value} value={option.value}>
                      {option.label}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* 查看详情弹窗 */}
      <Modal
        title="试剂/标准品详情"
        open={viewModalVisible}
        onCancel={() => setViewModalVisible(false)}
        footer={null}
        width={900}
      >
        {viewRecord && (
          <>
            {viewRecord.reagent_label_urls && viewRecord.reagent_label_urls.length > 0 && (
              <>
                <Divider>试剂标签图片</Divider>
                <Image.PreviewGroup>
                  <Space>
                    {viewRecord.reagent_label_urls.map((url, index) => (
                      <Image
                        key={index}
                        src={url}
                        width={100}
                        height={100}
                        style={{ objectFit: 'cover' }}
                      />
                    ))}
                  </Space>
                </Image.PreviewGroup>
              </>
            )}

            <Divider>基本信息</Divider>
            <Row gutter={16}>
              <Col span={8}>
                <strong>试剂名称：</strong>{viewRecord.reagent_name}
              </Col>
              <Col span={8}>
                <strong>批号：</strong>{viewRecord.lot_no}
              </Col>
              <Col span={8}>
                <strong>分类：</strong>
                {REAGENT_CATEGORY_OPTIONS.find((o) => o.value === viewRecord.category)?.label}
              </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 12 }}>
              <Col span={8}>
                <strong>规格：</strong>{viewRecord.specification || '-'}
              </Col>
              <Col span={8}>
                <strong>含量：</strong>{viewRecord.content || '-'}
              </Col>
              <Col span={8}>
                <strong>生产厂家：</strong>{viewRecord.manufacturer || '-'}
              </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 12 }}>
              <Col span={8}>
                <strong>到货日期：</strong>
                {viewRecord.arrival_date ? dayjs(viewRecord.arrival_date).format('YYYY-MM-DD') : '-'}
              </Col>
              <Col span={8}>
                <strong>生产日期：</strong>
                {viewRecord.production_date ? dayjs(viewRecord.production_date).format('YYYY-MM-DD') : '-'}
              </Col>
              <Col span={8}>
                <strong>有效期：</strong>
                {viewRecord.expiration_date ? dayjs(viewRecord.expiration_date).format('YYYY-MM-DD') : '-'}
              </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 12 }}>
              <Col span={8}>
                <strong>编号：</strong>{viewRecord.reagent_no || '-'}
              </Col>
              <Col span={8}>
                <strong>入场批号：</strong>{viewRecord.incoming_lot_no || '-'}
              </Col>
              <Col span={8}>
                <strong>数量：</strong>{viewRecord.quantity} {viewRecord.unit}
              </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 12 }}>
              <Col span={8}>
                <strong>状态：</strong>
                <Tag color={STATUS_COLORS[viewRecord.status]}>
                  {REAGENT_STATUS_OPTIONS.find((o) => o.value === viewRecord.status)?.label}
                </Tag>
              </Col>
              <Col span={8}>
                <strong>创建人：</strong>{viewRecord.created_by || '-'}
              </Col>
              <Col span={8}>
                <strong>创建时间：</strong>
                {viewRecord.created_at ? dayjs(viewRecord.created_at).format('YYYY-MM-DD HH:mm') : '-'}
              </Col>
            </Row>
          </>
        )}
      </Modal>
    </div>
  )
}
