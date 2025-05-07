# utils/pdf_generator.py - PDF 생성 기능
# 형식: Python (.py)
# 역할: 진단 결과 기반으로 PDF 보고서 생성

import os
import time
from datetime import datetime
from io import BytesIO
from typing import Dict, List, Any, Tuple, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image, PageBreak, ListFlowable, ListItem, Flowable
)
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.spider import SpiderChart

# 설정 로드
from config import REPORT_TITLE, COMPANY_NAME, LOGO_PATH

class PDFGenerator:
    """
    자가진단 결과와 개선 전략을 담은 PDF 보고서를 생성하는 클래스
    """
    
    def __init__(self):
        """PDF 생성기 초기화"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """사용자 정의 스타일 설정"""
        # 제목 스타일
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=20,
            textColor=colors.darkblue
        ))
        
        # 섹션 제목 스타일
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        
        # 서브섹션 제목 스타일
        self.styles.add(ParagraphStyle(
            name='SubsectionTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            textColor=colors.darkblue
        ))
        
        # 일반 텍스트 스타일
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8
        ))
        
        # 강조 스타일
        self.styles.add(ParagraphStyle(
            name='Emphasis',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        ))
        
        # 점수 테이블 스타일
        self.table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
    
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
    
    def _add_cover_page(self, elements: List, report_data: Dict[str, Any]):
        """표지 페이지 추가"""
        # 로고 추가 (있는 경우)
        if os.path.exists(LOGO_PATH):
            logo = Image(LOGO_PATH)
            logo.drawHeight = 3*cm
            logo.drawWidth = 8*cm
            elements.append(logo)
            elements.append(Spacer(1, 2*cm))
        
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
        paragraphs = overview.split('\n\n')
        for p in paragraphs:
            if p.strip():
                elements.append(Paragraph(p, self.styles['CustomBody']))
                elements.append(Spacer(1, 3*mm))
        
        elements.append(Spacer(1, 5*mm))
        
        # 레이더 차트 추가
        radar_chart = self._create_radar_chart(diagnosis_result)
        elements.append(radar_chart)
    
    def _add_score_analysis(self, elements: List, diagnosis_result: Dict[str, Any]):
        """점수 분석 섹션 추가"""
        elements.append(Paragraph("2. 점수 분석", self.styles['SectionTitle']))
        elements.append(Spacer(1, 5*mm))
        
        # 종합 점수 정보
        avg_score = diagnosis_result.get("avg_score", 0)
        level = diagnosis_result.get("level", {}).get("name", "")
        level_description = diagnosis_result.get("level", {}).get("description", "")
        
        elements.append(Paragraph(f"종합 점수: {avg_score}/5", self.styles['Emphasis']))
        elements.append(Paragraph(f"진단 레벨: {level}", self.styles['Emphasis']))
        elements.append(Spacer(1, 3*mm))
        elements.append(Paragraph(level_description, self.styles['CustomBody']))
        elements.append(Spacer(1, 1*cm))
        
        # 영역별 점수 테이블
        elements.append(Paragraph("영역별 점수", self.styles['SubsectionTitle']))
        elements.append(Spacer(1, 5*mm))
        
        stage_scores = diagnosis_result.get("stage_scores", {})
        
        # 테이블 헤더
        table_data = [["영역", "평균 점수", "최대 점수", "달성률"]]
        
        # 테이블 데이터
        for stage, score_info in stage_scores.items():
            avg_score = score_info.get("avg_score", 0)
            max_score = 5  # 최대 점수는 5점
            percentage = (avg_score / max_score) * 100
            
            table_data.append([
                stage,
                f"{avg_score}/5",
                f"{max_score}",
                f"{percentage:.1f}%"
            ])
        
        # 테이블 스타일 설정 및 추가
        score_table = Table(table_data, colWidths=[5*cm, 3*cm, 3*cm, 3*cm])
        score_table.setStyle(self.table_style)
        elements.append(score_table)
        
        elements.append(Spacer(1, 1*cm))
        
        # 바 차트 추가
        bar_chart = self._create_bar_chart(stage_scores)
        elements.append(bar_chart)
    
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
                    if current_section:
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
        
        # 목록 항목 생성
        list_items = []
        for item in items:
            list_items.append(ListItem(Paragraph(item, self.styles['CustomBody'])))
        
        # 목록 생성 및 추가
        bullet_list = ListFlowable(list_items, bulletType='bullet')
        elements.append(bullet_list)
        elements.append(Spacer(1, 5*mm))
    
    def _create_radar_chart(self, diagnosis_result: Dict[str, Any]) -> Drawing:
        """레이더 차트(거미줄 차트) 생성"""
        drawing = Drawing(400, 300)
        
        # 레이더 차트 생성
        chart = SpiderChart()
        chart.width = 300
        chart.height = 300
        chart.x = 50
        chart.y = 0
        
        # 영역별 점수 데이터
        stage_scores = diagnosis_result.get("stage_scores", {})
        
        # 차트 데이터 구성
        data = [[]]
        stage_names = []
        
        for stage, score_info in stage_scores.items():
            stage_names.append(stage)
            data[0].append(score_info.get("avg_score", 0))
        
        chart.data = data
        chart.labels = stage_names
        
        # 차트 스타일 설정
        chart.strands[0].strokeColor = colors.darkblue
        chart.strands[0].fillColor = colors.lightblue
        chart.strands[0].strokeWidth = 1
        chart.fillColor = colors.white
        
        chart.strandLabels.fontName = 'Helvetica'
        chart.strandLabels.fontSize = 8
        
        chart.strandLabels.boxAnchor = 'sw'
        chart.strandLabels.boxStrokeColor = colors.transparent
        chart.strandLabels.boxFillColor = colors.transparent
        
        chart.spokes.strokeColor = colors.lightgrey
        chart.spokes.strokeWidth = 0.5
        
        chart.spokeLabels.fontName = 'Helvetica'
        chart.spokeLabels.fontSize = 8
        
        # 최대값 설정 (5점 만점)
        chart.spokes.strokeDashArray = None
        chart.spokeLabels = None
        chart.strands[0].strokeWidth = 2
        chart.strands[0].fillColor = colors.lightblue.clone(alpha=0.4)
        
        # 차트 추가
        drawing.add(chart)
        
        # 제목 추가
        drawing.add(Paragraph("영역별 점수 분석", self.styles['SubsectionTitle']))
        
        return drawing
    
    def _create_bar_chart(self, stage_scores: Dict[str, Dict[str, Any]]) -> Drawing:
        """바 차트 생성"""
        drawing = Drawing(400, 300)
        
        # 바 차트 생성
        chart = VerticalBarChart()
        chart.width = 350
        chart.height = 200
        chart.x = 25
        chart.y = 50
        
        # 차트 데이터 구성
        data = [[]]
        stage_names = []
        
        for stage, score_info in stage_scores.items():
            stage_names.append(stage)
            data[0].append(score_info.get("avg_score", 0))
        
        chart.data = data
        chart.categoryAxis.categoryNames = stage_names
        
        # 차트 스타일 설정
        chart.bars[0].fillColor = colors.lightblue
        chart.bars[0].strokeColor = colors.darkblue
        chart.bars[0].strokeWidth = 1
        
        # Y축 설정 (0-5 점수 범위)
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = 5
        chart.valueAxis.valueStep = 1
        
        # 레이블 설정
        chart.categoryAxis.labels.angle = 30
        chart.categoryAxis.labels.boxAnchor = 'ne'
        chart.categoryAxis.labels.fontName = 'Helvetica'
        chart.categoryAxis.labels.fontSize = 8
        
        chart.valueAxis.labels.fontName = 'Helvetica'
        chart.valueAxis.labels.fontSize = 8
        
        # 차트 추가
        drawing.add(chart)
        
        # 제목 추가
        drawing.add(Paragraph("영역별 점수 차트", self.styles['SubsectionTitle']))
        
        return drawing

# 테스트 코드
if __name__ == "__main__":
    # 테스트 데이터
    test_diagnosis_result = {
        "total_score": 60,
        "avg_score": 3.0,
        "max_score": 100,
        "level": {
            "name": "발전 단계",
            "description": "플레이스 마케팅의 기본기가 잘 갖춰져 있습니다. 더 전략적인 접근으로 한 단계 발전시키세요."
        },
        "stage_scores": {
            "인식하게 한다": {"raw_score": 15, "avg_score": 3.75, "max_score": 20},
            "클릭하게 한다": {"raw_score": 11, "avg_score": 2.75, "max_score": 20},
            "머물게 한다": {"raw_score": 12, "avg_score": 3.0, "max_score": 20},
            "연락오게 한다": {"raw_score": 10, "avg_score": 2.5, "max_score": 20},
            "후속 피드백 받는다": {"raw_score": 12, "avg_score": 3.0, "max_score": 20}
        }
    }
    
    test_report_data = {
        "title": "네이버 스마트 플레이스 최적화 진단 보고서",
        "level": "발전 단계",
        "overview": "현재 플레이스 마케팅은 기본적인 요소들이 잘 갖춰져 있으나, 몇 가지 영역에서 개선이 필요합니다. 특히 클릭 유도와 전환율 향상 부분에 집중적인 노력이 필요합니다.\n\n강점 영역인 '인식하게 한다' 단계의 노하우를 다른 영역에도 적용하면 좋은 시너지 효과를 볼 수 있을 것으로 예상됩니다.",
        "strengths_analysis": "인식 단계에서 뛰어난 성과를 보이고 있습니다. 키워드 최적화와 상세 설명 작성이 잘 되어 있어 검색 노출에 유리한 상태입니다.\n\n이러한 강점을 활용하여 클릭률과 전환율을 높이는 방향으로 전략을 확장하면 좋은 결과를 얻을 수 있을 것입니다.",
        "improvements_analysis": "클릭 유도와 전환율 향상 부분이 다소 미흡합니다. 대표 이미지의 품질과 다양성을 높이고, CTA(행동 유도) 문구를 강화할 필요가 있습니다.\n\n또한 리뷰 관리와 단골 고객 프로그램을 체계화하면 후속 피드백 영역의 점수도 향상될 것으로 예상됩니다.",
        "action_plan": "클릭 유도 개선:\n1. 대표 이미지 품질 향상: 전문 사진작가를 통해 고품질 이미지 촬영\n2. 이미지 다양성 확보: 매장 외관, 내부, 메뉴, 서비스 과정을 모두 보여주는 사진 구성\n3. 캐치프레이즈 개발: 비즈니스의 핵심 가치를 담은 매력적인 한 줄 소개 추가\n\n전환율 향상:\n1. 스마트콜 응대 시스템 개선: 영업시간 동안 100% 응대율 유지\n2. 예약 시스템 활성화: 온라인 예약 시 특별 혜택 제공\n3. 전환 유도 문구 강화: '지금 예약하고 10% 할인받기' 등의 명확한 CTA 문구 사용"
    }
    
    # PDF 생성기 초기화
    pdf_generator = PDFGenerator()
    
    # 테스트 PDF 생성
    output_dir = "."  # 현재 디렉토리
    pdf_path = pdf_generator.generate_report(
        diagnosis_result=test_diagnosis_result,
        report_data=test_report_data,
        output_path=output_dir
    )
    
    print(f"테스트 PDF 생성 완료: {pdf_path}")