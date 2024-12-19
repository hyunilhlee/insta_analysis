import logging
from typing import List, Dict, Any
from pathlib import Path
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline
)

logger = logging.getLogger(__name__)

class LlamaAnalyzer:
    def __init__(self, model_path: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        """LlamaAnalyzer 초기화"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            low_cpu_mem_usage=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model.to(self.device)
        
    def _generate_response(self, prompt: str, max_new_tokens: int = 100, temperature: float = 0.7) -> str:
        """텍스트 생성 공통 함수"""
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(self.device)
        
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            pad_token_id=self.tokenizer.eos_token_id,
            num_return_sequences=1
        )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """텍스트에서 주요 키워드 추출"""
        try:
            prompt = f"""<human>다음 텍스트에서 가장 중요한 키워드 {max_keywords}개를 추출해주세요. 쉼표(,)로 구분해서 답변해주세요:

{text}

키워드:</human>
<assistant>"""
            
            response = self._generate_response(prompt, max_new_tokens=50)
            # 응답에서 키워드 부분만 추출
            if "키워드:" in response:
                keywords = response.split("키워드:")[-1].strip()
            else:
                keywords = response.split("<assistant>")[-1].strip()
            
            # 쉼표로 분리하고 정제
            keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
            return keyword_list[:max_keywords]
            
        except Exception as e:
            logger.error(f"키워드 추출 중 에러 발생: {str(e)}")
            return []
    
    def summarize_text(self, text: str) -> str:
        """텍스트 요약"""
        try:
            prompt = f"""<human>다음 텍스트를 2-4문장으로 요약해주세요:

{text}

요약:</human>
<assistant>"""
            
            response = self._generate_response(prompt, max_new_tokens=200)
            
            if "요약:" in response:
                summary = response.split("요약:")[-1].strip()
            else:
                summary = response.split("<assistant>")[-1].strip()
            
            return summary
            
        except Exception as e:
            logger.error(f"텍스트 요약 중 에러 발생: {str(e)}")
            return "텍스트 요약에 실패했습니다."
    
    def analyze_sentiment(self, text: str) -> str:
        """감정 분석"""
        try:
            prompt = f"""<human>다음 텍스트의 감정을 분석하여 '긍정', '중립', '부정' 중 하나로만 답변해주세요:

{text}

감정:</human>
<assistant>"""
            
            response = self._generate_response(prompt, max_new_tokens=50, temperature=0.3)
            
            if "감정:" in response:
                sentiment = response.split("감정:")[-1].strip()
            else:
                sentiment = response.split("<assistant>")[-1].strip()
            
            # 응답을 세 가지 감정 중 하나로 정규화
            sentiment = sentiment.lower()
            if "긍정" in sentiment:
                return "긍정"
            elif "부정" in sentiment:
                return "부정"
            else:
                return "중립"
            
        except Exception as e:
            logger.error(f"감정 분석 중 에러 발생: {str(e)}")
            return "알 수 없음"
    
    def analyze_content_relevance(self, text: str, image_description: str) -> str:
        """텍스트와 이미지 간의 관련성 분석"""
        try:
            prompt = f"""<human>다음 텍스트와 이미지 설명 간의 관련성을 분석해주세요:

텍스트: {text}

이미지 설명: {image_description}

관련성을 높음/중간/낮음 중 하나로 평가하고, 그 이유를 1-2문장으로 설명해주세요.</human>
<assistant>"""
            
            response = self._generate_response(prompt, max_new_tokens=150)
            
            if "관련성:" in response:
                relevance = response.split("관련성:")[-1].strip()
            else:
                relevance = response.split("<assistant>")[-1].strip()
            
            return relevance
            
        except Exception as e:
            logger.error(f"컨텐츠 관련성 분석 중 에러 발생: {str(e)}")
            return "컨텐츠 관련성 분석에 실패했습니다."
