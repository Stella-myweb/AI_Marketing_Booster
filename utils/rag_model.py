# utils/rag_model.py
import os
import streamlit as st
from typing import Dict, List, Any, Optional

# 외부 라이브러리
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

# 설정
from config import OPENAI_API_KEY, LLM_MODEL, TEMPERATURE, DATA_DIR

# ---------------------- 벡터스토어 ----------------------
class VectorStore:
    def __init__(self):
        try:
            api_key = st.secrets.get("OPENAI_API_KEY", OPENAI_API_KEY)
            if not api_key:
                st.error("OpenAI API 키가 설정되지 않았습니다.")
                raise ValueError("API 키가 없습니다")
            
            # API 키 유효성 검사
            try:
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=api_key,
                    model="text-embedding-ada-002"
                )
                # 간단한 임베딩 테스트
                self.embeddings.embed_query("test")
            except Exception as e:
                st.error(f"OpenAI API 키 유효성 검사 실패: {e}")
                raise ValueError("API 키가 유효하지 않습니다")
            
            self.data_dir = DATA_DIR
            vectorstore_path = os.path.join(self.data_dir, "vectorstore")
            
            # 벡터스토어 디렉토리 확인
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir, exist_ok=True)
                st.warning(f"데이터 디렉토리가 생성되었습니다: {self.data_dir}")
            
            if os.path.exists(vectorstore_path):
                try:
                    self.vectorstore = FAISS.load_local(vectorstore_path, self.embeddings)
                    st.success("벡터스토어를 성공적으로 로드했습니다.")
                except Exception as e:
                    st.warning(f"기존 벡터스토어 로드 실패, 새로 생성합니다: {e}")
                    self._create_vectorstore()
            else:
                st.info("벡터스토어를 새로 생성합니다...")
                self._create_vectorstore()
                
        except Exception as e:
            st.error(f"벡터 스토어 초기화 오류: {e}")
            raise

    def _create_vectorstore(self):
        try:
            content_dir = os.path.join(self.data_dir, "content")
            if not os.path.exists(content_dir):
                os.makedirs(content_dir, exist_ok=True)
                st.info(f"콘텐츠 디렉토리가 생성되었습니다: {content_dir}")
            
            text_files = [os.path.join(root, file)
                         for root, _, files in os.walk(content_dir)
                         for file in files if file.endswith(".txt")]
            
            ebook_file = os.path.join(self.data_dir, "ebook_content.txt")
            if os.path.exists(ebook_file):
                text_files.append(ebook_file)
            
            if not text_files:
                default_file = os.path.join(content_dir, "default_content.txt")
                with open(default_file, "w", encoding="utf-8") as f:
                    f.write("""
                    네이버 스마트 플레이스 최적화를 위한 기본 가이드:
                    1. 정확한 기본 정보 입력하기
                    2. 매력적인 이미지 사용하기
                    3. 키워드 최적화하기
                    4. 고객 리뷰 관리하기
                    5. 정기적인 업데이트하기
                    """)
                text_files.append(default_file)
                st.info("기본 콘텐츠 파일이 생성되었습니다.")
            
            documents = []
            for file_path in text_files:
                try:
                    loader = TextLoader(file_path, encoding="utf-8")
                    documents.extend(loader.load())
                    st.success(f"파일 로드 성공: {os.path.basename(file_path)}")
                except Exception as e:
                    st.warning(f"파일 로드 오류 ({file_path}): {e}")
            
            if not documents:
                raise ValueError("로드할 수 있는 문서가 없습니다.")
            
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            split_documents = text_splitter.split_documents(documents)
            
            self.vectorstore = FAISS.from_documents(split_documents, self.embeddings)
            vectorstore_path = os.path.join(self.data_dir, "vectorstore")
            self.vectorstore.save_local(vectorstore_path)
            st.success("벡터스토어가 성공적으로 생성되었습니다.")
            
        except Exception as e:
            st.error(f"벡터스토어 생성 중 오류: {e}")
            raise

    def get_relevant_content(self, query: str, n_results: int = 3) -> str:
        try:
            docs = self.vectorstore.similarity_search(query, k=n_results)
            context = "\n\n".join([doc.page_content for doc in docs])
            return context
        except Exception as e:
            st.error(f"콘텐츠 검색 오류: {e}")
            return "콘텐츠 검색 중 오류가 발생했습니다."

    def raw_similarity_search(self, query: str, k: int = 5):
        try:
            if not query:
                return []
            docs = self.vectorstore.similarity_search(query, k=k)
            return docs
        except Exception as e:
            st.error(f"유사 문서 검색 오류: {e}")
            return []

# ---------------------- 질문/진단 유틸리티 (간략화) ----------------------
# 실제 서비스에서는 questions.py에서 import 하거나, 아래처럼 필요한 함수만 포함

def suggest_improvements(result):
    # 예시: 개선점 추천 (실제 로직은 questions.py 참고)
    return ["키워드 다양화", "이미지 품질 개선", "리뷰 관리 강화"]

# ---------------------- RAG 모델 통합 ----------------------
class RAGModel:
    def __init__(self):
        try:
            api_key = st.secrets.get("OPENAI_API_KEY", OPENAI_API_KEY)
            if not api_key:
                st.error("OpenAI API 키가 설정되지 않았습니다.")
                raise ValueError("API 키가 없습니다")
            
            # API 키 유효성 검사
            try:
                self.llm = ChatOpenAI(
                    openai_api_key=api_key,
                    model_name=LLM_MODEL,
                    temperature=TEMPERATURE
                )
                # 간단한 테스트 쿼리
                self.llm.predict("test")
            except Exception as e:
                st.error(f"OpenAI API 키 유효성 검사 실패: {e}")
                raise ValueError("API 키가 유효하지 않습니다")
            
            # 벡터스토어 초기화
            try:
                self.vector_store = VectorStore()
                st.success("RAG 모델이 성공적으로 초기화되었습니다.")
            except Exception as e:
                st.error(f"벡터스토어 초기화 실패: {e}")
                raise ValueError("벡터스토어 초기화에 실패했습니다")
                
        except Exception as e:
            st.error(f"RAG 모델 초기화 오류: {e}")
            self.llm = None
            self.vector_store = None
            raise

    def generate_response(self, query: str, context: str = None, n_results: int = 3) -> str:
        """
        쿼리에 대한 전문적이고 구체적인 답변을 생성합니다. (1000자 이내, 이모티콘 소제목)
        """
        try:
            if not context and self.vector_store:
                context = self.vector_store.get_relevant_content(query, n_results=n_results)
            elif not context:
                context = """
                네이버 스마트 플레이스 최적화 일반 팁:
                1. 매력적인 이미지 사용하기
                2. 핵심 키워드 포함하기
                3. 상세한 비즈니스 설명 제공하기
                4. 정기적인 콘텐츠 업데이트하기
                5. 고객 리뷰 관리하기
                """
            prompt = f"""
            당신은 네이버 스마트 플레이스 최적화 전문가입니다. 아래 질문에 대해 1000자 이내로, 실제 사례와 통계, 최신 트렌드를 반영하여 전문적으로 답변하세요. 각 소제목은 이모티콘(예: # 📊, # 🎯, # 💡)으로 구분해 주세요.

            참고 자료:
            {context}

            질문: {query}

            답변 형식 예시:
            # 📊 현황 분석\n(현황)
            # 🎯 핵심 전략\n(전략)
            # 💡 실전 팁\n(팁)

            답변:
            """
            response = self.llm.predict(prompt)
            return response[:1000]  # 1000자 이내로 제한
        except Exception as e:
            st.error(f"응답 생성 중 오류: {e}")
            return "응답 생성 중 오류가 발생했습니다. 다시 시도해주세요."

    def generate_diagnosis_report(self, answers: Dict[str, str], diagnosis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        자가진단 결과를 바탕으로 각 소제목별로 전문적 분석을 생성합니다.
        """
        try:
            level = diagnosis_result.get("level", {}).get("name", "기본")
            improvements = diagnosis_result.get("improvements", {})
            weak_areas = [area['stage'] for area in improvements.get('weak_areas', [])]
            strong_areas = [area['stage'] for area in improvements.get('strong_areas', [])]
            area_contexts = {}
            
            if self.vector_store:
                # 약점 영역과 강점 영역 모두에 대한 컨텍스트 수집
                for area in set(weak_areas + strong_areas):
                    query = f"네이버 스마트 플레이스 {area} 전략과 성공 사례"
                    area_contexts[area] = self.vector_store.get_relevant_content(query, n_results=2)
            
            title_map = {
                "인식하게 한다": "검색 노출 최적화",
                "클릭하게 한다": "클릭율 높이는 전략",
                "머물게 한다": "체류시간 늘리는 방법",
                "연락오게 한다": "문의/예약 전환율 높이기",
                "후속 피드백 받는다": "고객 재방문 유도 전략"
            }

            # 각 소제목별로 따로 프롬프트 생성
            prompts = {
                "overview": f"""
                당신은 네이버 스마트 플레이스 최적화 전문가입니다. 아래 진단 결과를 바탕으로\n# 📊 종합 진단\n
                1. 현재 상태: {level} 레벨로 진단되었습니다.
                2. 강점 영역: {', '.join([title_map.get(area, area) for area in strong_areas[:2]])}
                3. 개선 영역: {', '.join([title_map.get(area, area) for area in weak_areas[:2]])}
                
                800자 이내로 다음 내용을 포함하여 종합적인 진단 분석을 작성해주세요:
                - 현재 스마트 플레이스 운영의 전반적인 수준
                - 강점 영역에서의 우수한 점
                - 개선 영역에서의 주요 과제
                - 향후 발전 방향
                
                참고 자료:
                {'\\n'.join([area_contexts.get(area, '') for area in weak_areas[:2] + strong_areas[:2]])}
                """,
                
                "strengths_analysis": f"""
                당신은 네이버 스마트 플레이스 최적화 전문가입니다. 아래 진단 결과를 바탕으로\n# 💪 강점 분석\n
                1. 강점 영역: {', '.join([title_map.get(area, area) for area in strong_areas[:2]])}
                2. 진단 레벨: {level}
                
                800자 이내로 다음 내용을 포함하여 강점 분석을 작성해주세요:
                - 각 강점 영역별 세부 분석
                - 현재 잘 하고 있는 점
                - 강점을 더욱 강화할 수 있는 방안
                - 경쟁사 대비 우위 요소
                
                참고 자료:
                {'\\n'.join([area_contexts.get(area, '') for area in strong_areas[:2]])}
                """,
                
                "improvements_analysis": f"""
                당신은 네이버 스마트 플레이스 최적화 전문가입니다. 아래 진단 결과를 바탕으로\n# 🎯 개선점 분석\n
                1. 개선 영역: {', '.join([title_map.get(area, area) for area in weak_areas[:2]])}
                2. 진단 레벨: {level}
                
                800자 이내로 다음 내용을 포함하여 개선점 분석을 작성해주세요:
                - 각 개선 영역별 세부 분석
                - 현재 부족한 점
                - 개선이 필요한 이유
                - 개선 시 기대 효과
                
                참고 자료:
                {'\\n'.join([area_contexts.get(area, '') for area in weak_areas[:2]])}
                """,
                
                "action_plan": f"""
                당신은 네이버 스마트 플레이스 최적화 전문가입니다. 아래 진단 결과를 바탕으로\n# 📝 액션 플랜\n
                1. 개선 영역: {', '.join([title_map.get(area, area) for area in weak_areas[:2]])}
                2. 진단 레벨: {level}
                
                800자 이내로 다음 내용을 포함하여 구체적인 액션 플랜을 작성해주세요:
                - 단기 실행 계획 (1-2주)
                - 중기 실행 계획 (1-3개월)
                - 장기 실행 계획 (3-6개월)
                - 각 단계별 구체적인 실행 방안
                - 예상되는 결과와 효과
                
                참고 자료:
                {'\\n'.join([area_contexts.get(area, '') for area in weak_areas[:2]])}
                """,
                
                "upgrade_tips": f"""
                당신은 네이버 스마트 플레이스 최적화 전문가입니다. 아래 진단 결과를 바탕으로\n# 💡 고급 전략 팁\n
                1. 진단 레벨: {level}
                2. 강점 영역: {', '.join([title_map.get(area, area) for area in strong_areas[:2]])}
                3. 개선 영역: {', '.join([title_map.get(area, area) for area in weak_areas[:2]])}
                
                800자 이내로 다음 내용을 포함하여 고급 전략 팁을 작성해주세요:
                - 경쟁사와의 차별화 전략
                - 최신 트렌드 활용 방안
                - 고객 경험 향상 팁
                - ROI를 높이는 실전 전략
                
                참고 자료:
                {'\\n'.join([area_contexts.get(area, '') for area in weak_areas[:2] + strong_areas[:2]])}
                """
            }
            
            results = {}
            for key, prompt in prompts.items():
                results[key] = self.llm.predict(prompt)[:800]
            
            return {
                "title": "네이버 스마트 플레이스 최적화 전략 가이드",
                "level": level,
                "overview": results["overview"],
                "strengths_analysis": results["strengths_analysis"],
                "improvements_analysis": results["improvements_analysis"],
                "action_plan": results["action_plan"],
                "upgrade_tips": results["upgrade_tips"]
            }
        except Exception as e:
            st.error(f"진단 보고서 생성 중 오류: {e}")
            return {
                "title": "네이버 스마트 플레이스 최적화 전략 가이드",
                "level": diagnosis_result.get("level", {}).get("name", "기본"),
                "overview": "진단 결과 생성에 실패했습니다.",
                "strengths_analysis": "진단 결과 생성에 실패했습니다.",
                "improvements_analysis": "진단 결과 생성에 실패했습니다.",
                "action_plan": "진단 결과 생성에 실패했습니다.",
                "upgrade_tips": "진단 결과 생성에 실패했습니다."
            }

    def search_ebook_content(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        try:
            if self.vector_store is None:
                return [{"content": "이북 데이터를 사용할 수 없습니다.", "source": "시스템"}]
            docs = self.vector_store.raw_similarity_search(query, n_results)
            results = []
            for i, doc in enumerate(docs):
                results.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", f"이북 섹션 {i+1}"),
                    "relevance": round((1.0 - (i * 0.1)), 2)
                })
            return results
        except Exception as e:
            st.error(f"이북 콘텐츠 검색 오류: {e}")
            return [{"content": "검색 중 오류가 발생했습니다.", "source": "시스템"}]

__all__ = ['RAGModel'] 
