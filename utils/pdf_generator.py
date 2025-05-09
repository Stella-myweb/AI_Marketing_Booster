import os
import time
from datetime import datetime
from io import BytesIO
from typing import Dict, List, Any, Tuple, Optional

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image, PageBreak, ListFlowable, ListItem
)

# 설정 로드
from config import REPORT_TITLE, COMPANY_NAME, LOGO_PATH

class PDFGenerator:
    """
    자가진단 결과와 개선 전략을 담은 PDF 보고서를 생성하는 클래스
    """
    
    def __init__(self):
        """PDF 생성기 초기화"""
        self.styles = getSampleStyleSheet()
        self._register_fonts()
        self._setup_custom_styles()
    
    def _register_fonts(self):
        """한글 폰트 등록"""
        try:
            # 프로젝트 내 폰트 파일 경로 (assets/fonts/ 디렉토리에 폰트 파일을 복사해야 함)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(base_dir)  # utils 폴더의 상위 디렉토리 (프로젝트 루트)
            
            # 각 폰트 파일 경로
            malgun_path = os.path.join(project_root, 'assets', 'fonts', 'malgun.ttf')
            malgunbd_path = os.path.join(project_root, 'assets', 'fonts', 'malgunbd.ttf')
            malgunsl_path = os.path.join(project_root, 'assets', 'fonts', 'malgunsl.ttf')
            
            # 폰트 등록
            if os.path.exists(malgun_path):
                pdfmetrics.registerFont(TTFont('Malgun', malgun_path))
                print(f"폰트 등록 성공: Malgun")
            else:
                print(f"경고: 폰트 파일을 찾을 수 없습니다: {malgun_path}")
            
            if os.path.exists(malgunbd_path):
                pdfmetrics.registerFont(TTFont('MalgunBold', malgunbd_path))
                print(f"폰트 등록 성공: MalgunBold")
            else:
                print(f"경고: 폰트 파일을 찾을 수 없습니다: {malgunbd_path}")
            
            if os.path.exists(malgunsl_path):
                pdfmetrics.registerFont(TTFont('MalgunSemilight', malgunsl_path))
                print(f"폰트 등록 성공: MalgunSemilight")
            else:
                print(f"경고: 폰트 파일을 찾을 수 없습니다: {malgunsl_path}")
            
            # 폰트 패밀리 등록
            pdfmetrics.registerFontFamily(
                'Malgun',
                normal='Malgun',
                bold='MalgunBold',
                italic='Malgun',
                boldItalic='MalgunBold'
            )
        except Exception as e:
            print(f"폰트 등록 중 오류 발생: {str(e)}")
            print("기본 폰트를 사용합니다.")
    
    def _setup_custom_styles(self):
        """사용자 정의 스타일 설정"""
        # 제목 스타일
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontName='Malgun',  # 한글 폰트 사용
            fontSize=24,
            spaceAfter=20,
            textColor=colors.darkblue
        ))
        
        # 섹션 제목 스타일
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading1'],
            fontName='MalgunBold',  # 한글 볼드체 사용
            fontSize=18,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        
        # 서브섹션 제목 스타일
        self.styles.add(ParagraphStyle(
            name='SubsectionTitle',
            parent=self.styles['Heading2'],
            fontName='MalgunBold',  # 한글 볼드체 사용
            fontSize=14,
            spaceAfter=10,
            textColor=colors.darkblue
        ))
        
        # 일반 텍스트 스타일
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontName='Malgun',  # 한글 폰트 사용
            fontSize=11,
            spaceAfter=8
        ))
        
        # 강조 스타일
        self.styles.add(ParagraphStyle(
            name='Emphasis',
            parent=self.styles['Normal'],
            fontName='MalgunBold',  # 한글 볼드체 사용
            fontSize=11,
            spaceAfter=8,
            textColor=colors.darkblue
        ))
        
        # 점수 테이블 스타일
        self.table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'MalgunBold'),  # 헤더에 볼드체
            ('FONTNAME', (0, 1), (-1, -1), 'Malgun'),     # 내용에 일반체
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
    
    def _get_page_break(self):
        """페이지 브레이크 요소 반환"""
        return PageBreak()
    
    def generate_report(self, 
                       diagnosis_result: Dict[str, Any], 
                       report_data: Dict[str, Any], 
                       output_path: str) -> str:
        """
        진단 결과 및 보고서 데이터를 바탕으로 PDF 보고서를 생성합니다.
        
        Args:
            diagnosis_result: 자가진단 계산 결과
            report_data: RAG 모델에서 생성한 보고서 데이터
            output_path: PDF 저장 경로
            
        Returns:
            생성된 PDF 파일 경로
        """
        # 저장 경로가 존재하는지 확인
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
            except Exception as e:
                print(f"디렉토리 생성 중 오류 발생: {str(e)}")
                return ""
        
        # 현재 시간을 파일명에 포함
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_path}/place_optimization_report_{timestamp}.pdf"
        
        # PDF 문서 생성
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # 요소 목록 초기화
        elements = []
        
        try:
            # 표지 추가
            self._add_cover_page(elements, report_data)
            elements.append(PageBreak())
            
            # 목차 추가
            self._add_table_of_contents(elements)
            elements.append(PageBreak())
            
            # 진단 개요 추가
            self._add_overview_section(elements, diagnosis_result, report_data)
            elements.append(PageBreak())
            
            # 점수 분석 추가
            self._add_score_analysis(elements, diagnosis_result)
            elements.append(PageBreak())
            
            # 강점 분석 추가
            self._add_strengths_analysis(elements, report_data)
            elements.append(PageBreak())
            
            # 개선점 분석 추가
            self._add_improvements_analysis(elements, report_data)
            elements.append(PageBreak())
            
            # 액션 플랜 추가
            self._add_action_plan(elements, report_data)
            
            # PDF 생성
            doc.build(elements)
            print(f"PDF 보고서가 생성되었습니다: {filename}")
            
            return filename
        except Exception as e:
            print(f"PDF 생성 중 오류 발생: {str(e)}")
            return ""
    
    def _add_cover_page(self, elements: List, report_data: Dict[str, Any]):
        """표지 페이지 추가"""
        # 로고 추가 (있는 경우)
        try:
            if os.path.exists(LOGO_PATH):
                logo = Image(LOGO_PATH)
                logo.drawHeight = 3*cm
                logo.drawWidth = 8*cm
                elements.append(logo)
                elements.append(Spacer(1, 2*cm))
        except Exception as e:
            print(f"로고 추가 중 오류: {str(e)}")
            # 로고 추가에 실패해도 계속 진행
        
        # 제목 추가
        elements.append(Paragraph(REPORT_TITLE, self.styles['CustomTitle']))
        elements.append(Spacer(1, 1*cm))
        
        # 진단 일자 추가
        date_str = datetime.now().strftime("%Y년 %m월 %d일")
        elements.append(Paragraph(f"진단일: {date_str}", self.styles['CustomBody']))
        elements.append(Spacer(1, 5*mm))
        
        # 레벨 정보 추가
        level = report_data.get("level", "")
        elements.append(Paragraph(f"진단 레벨: {level}", self.styles['Emphasis']))
        elements.append(Spacer(1, 3*cm))
        
        # 회사 정보 추가
        elements.append(Paragraph(f"제공: {COMPANY_NAME}", self.styles['CustomBody']))
    
    def _add_table_of_contents(self, elements: List):
        """목차 추가"""
        elements.append(Paragraph("목차", self.styles['SectionTitle']))
        elements.append(Spacer(1, 1*cm))
        
        toc_items = [
            ("1. 진단 개요", "네이버 스마트 플레이스 최적화 상태에 대한 종합적인 평가"),
            ("2. 점수 분석", "영역별 점수와 레벨 평가"),
            ("3. 강점 분석", "잘하고 있는 영역과 활용 방안"),
            ("4. 개선점 분석", "개선이 필요한 영역과 기대 효과"),
            ("5. 액션 플랜", "구체적인 개선 전략과 실행 방법")
        ]
        
        # 목차 테이블 생성
        toc_data = []
        for title, description in toc_items:
            toc_data.append([
                Paragraph(title, self.styles['CustomBody']),
                Paragraph(description, self.styles['CustomBody'])
            ])
        
        toc_table = Table(toc_data, colWidths=[5*cm, 10*cm])
        toc_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(toc_table)
    
    def _add_overview_section(self, elements: List, diagnosis_result: Dict[str, Any], report_data: Dict[str, Any]):
        """진단 개요 섹션 추가"""
        elements.append(Paragraph("1. 진단 개요", self.styles['SectionTitle']))
        elements.append(Spacer(1, 5*mm))
        
        # 개요 내용
        overview = report_data.get("overview", "")
        if not overview or overview.strip() == "":
            overview = "본 보고서는 네이버 스마트 플레이스 최적화 상태에 대한 종합적인 평가를 담고 있습니다."
            
        paragraphs = overview.split('\n\n')
        for p in paragraphs:
            if p.strip():
                elements.append(Paragraph(p, self.styles['CustomBody']))
                elements.append(Spacer(1, 3*mm))
        
        elements.append(Spacer(1, 5*mm))
        
        # 영역별 점수 분석 섹션 제목
        elements.append(Paragraph("영역별 점수 분석", self.styles['SubsectionTitle']))
        elements.append(Spacer(1, 5*mm))
        
        # 테이블 형태로 영역별 점수 표시
        stage_scores = diagnosis_result.get("stage_scores", {})
        if stage_scores:
            # 테이블 데이터 구성
            table_data = [["영역", "점수"]]
            for stage, score_info in stage_scores.items():
                avg_score = score_info.get("avg_score", 0)
                table_data.append([stage, f"{avg_score}/5"])
            
            # 테이블 생성
            score_table = Table(table_data, colWidths=[10*cm, 5*cm])
            score_table.setStyle(self.table_style)
            elements.append(score_table)
        else:
            elements.append(Paragraph("영역별 점수 정보가 없습니다.", self.styles['CustomBody']))
    
    def _add_score_analysis(self, elements: List, diagnosis_result: Dict[str, Any]):
        """점수 분석 섹션 추가"""
        elements.append(Paragraph("2. 점수 분석", self.styles['SectionTitle']))
        elements.append(Spacer(1, 5*mm))
        
        # 종합 점수 정보
        avg_score = diagnosis_result.get("avg_score", 0)
        level = diagnosis_result.get("level", {})
        level_name = level.get("name", "") if isinstance(level, dict) else ""
        level_description = level.get("description", "") if isinstance(level, dict) else ""
        
        elements.append(Paragraph(f"종합 점수: {avg_score}/5", self.styles['Emphasis']))
        elements.append(Paragraph(f"진단 레벨: {level_name}", self.styles['Emphasis']))
        elements.append(Spacer(1, 3*mm))
        elements.append(Paragraph(level_description, self.styles['CustomBody']))
        elements.append(Spacer(1, 1*cm))
        
        # 영역별 점수 테이블
        elements.append(Paragraph("영역별 점수", self.styles['SubsectionTitle']))
        elements.append(Spacer(1, 5*mm))
        
        stage_scores = diagnosis_result.get("stage_scores", {})
        
        if stage_scores:
            # 테이블 헤더
            table_data = [["영역", "평균 점수", "최대 점수", "달성률"]]
            
            # 테이블 데이터
            for stage, score_info in stage_scores.items():
                if not isinstance(score_info, dict):
                    continue
                    
                avg_score = score_info.get("avg_score", 0)
                max_score = 5  # 최대 점수는 5점
                percentage = (avg_score / max_score) * 100 if max_score > 0 else 0
                
                table_data.append([
                    stage,
                    f"{avg_score}/5",
                    f"{max_score}",
                    f"{percentage:.1f}%"
                ])
            
            # 테이블 스타일 설정 및 추가
            if len(table_data) > 1:  # 헤더만 있는 경우 제외
                score_table = Table(table_data, colWidths=[5*cm, 3*cm, 3*cm, 3*cm])
                score_table.setStyle(self.table_style)
                elements.append(score_table)
            else:
                elements.append(Paragraph("영역별 점수 정보가 없습니다.", self.styles['CustomBody']))
        else:
            elements.append(Paragraph("영역별 점수 정보가 없습니다.", self.styles['CustomBody']))
    
    def _add_strengths_analysis(self, elements: List, report_data: Dict[str, Any]):
        """강점 분석 섹션 추가"""
        elements.append(Paragraph("3. 강점 분석", self.styles['SectionTitle']))
        elements.append(Spacer(1, 5*mm))
        
        # 강점 분석 내용
        strengths_analysis = report_data.get("strengths_analysis", "")
        
        if not strengths_analysis or strengths_analysis.strip() == "":
            elements.append(Paragraph(
                "현재 플레이스 마케팅에서 특별히 뛰어난 강점 영역은 식별되지 않았습니다. "
                "모든 영역에서 체계적인 개선이 필요합니다.",
                self.styles['CustomBody']
            ))
        else:
            # 문단별로 처리
            paragraphs = strengths_analysis.split('\n\n')
            for p in paragraphs:
                if p.strip():
                    elements.append(Paragraph(p, self.styles['CustomBody']))
                    elements.append(Spacer(1, 3*mm))
    
    def _add_improvements_analysis(self, elements: List, report_data: Dict[str, Any]):
        """개선점 분석 섹션 추가"""
        elements.append(Paragraph("4. 개선점 분석", self.styles['SectionTitle']))
        elements.append(Spacer(1, 5*mm))
        
        # 개선점 분석 내용
        improvements_analysis = report_data.get("improvements_analysis", "")
        
        if not improvements_analysis or improvements_analysis.strip() == "":
            elements.append(Paragraph(
                "현재 특별히 개선이 필요한 약점 영역은 식별되지 않았습니다. "
                "전반적으로 균형 잡힌 플레이스 마케팅을 하고 있습니다.",
                self.styles['CustomBody']
            ))
        else:
            # 문단별로 처리
            paragraphs = improvements_analysis.split('\n\n')
            for p in paragraphs:
                if p.strip():
                    elements.append(Paragraph(p, self.styles['CustomBody']))
                    elements.append(Spacer(1, 3*mm))
    
    def _add_action_plan(self, elements: List, report_data: Dict[str, Any]):
        """액션 플랜 섹션 추가"""
        elements.append(Paragraph("5. 액션 플랜", self.styles['SectionTitle']))
        elements.append(Spacer(1, 5*mm))
        
        # 액션 플랜 내용
        action_plan = report_data.get("action_plan", "")
        
        if not action_plan or action_plan.strip() == "":
            elements.append(Paragraph(
                "현재 액션 플랜을 생성할 수 없습니다. 더 자세한 진단 정보가 필요합니다.",
                self.styles['CustomBody']
            ))
        else:
            # 문단별로 처리해서 목록 항목 식별
            lines = action_plan.split('\n')
            current_section = None
            current_items = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 새로운 섹션 시작 (영역명: 으로 시작하는 줄)
                if ':' in line and len(line.split(':')[0].split()) <= 3:
                    # 이전 섹션이 있으면 먼저 처리
                    if current_section and current_items:
                        self._add_action_section(elements, current_section, current_items)
                        current_items = []
                    
                    current_section = line
                    elements.append(Paragraph(line, self.styles['SubsectionTitle']))
                
                # 숫자나 글머리 기호로 시작하는 항목
                elif line.startswith(('1.', '2.', '3.', '4.', '5.', '•', '-', '*')):
                    current_items.append(line)
                
                # 일반 문단
                else:
                    elements.append(Paragraph(line, self.styles['CustomBody']))
            
            # 마지막 섹션 처리
            if current_section and current_items:
                self._add_action_section(elements, current_section, current_items)
    
    def _add_action_section(self, elements: List, section_title: str, items: List[str]):
        """액션 플랜 섹션 내 항목들 추가"""
        if not items:
            return
        
        try:
            # 목록 항목 생성
            list_items = []
            for item in items:
                # 선행 기호나 숫자 제거 (필요 시)
                if item.startswith(('1.', '2.', '3.', '4.', '5.')):
                    cleaned_item = item[2:].strip()
                elif item.startswith(('•', '-', '*')):
                    cleaned_item = item[1:].strip()
                else:
                    cleaned_item = item

                list_items.append(ListItem(Paragraph(cleaned_item, self.styles['CustomBody'])))
            
            # 목록 생성 및 추가
            bullet_list = ListFlowable(list_items, bulletType='bullet')
            elements.append(bullet_list)
            elements.append(Spacer(1, 5*mm))
        except Exception as e:
            print(f"액션 플랜 섹션 처리 중 오류: {str(e)}")
            # 오류 발생 시 일반 문단으로 추가
            for item in items:
                elements.append(Paragraph(item, self.styles['CustomBody']))
                elements.append(Spacer(1, 2*mm)) 