"""
Emotion analysis module using ML models and keyword fallback
"""

from config import EMOTION_MODEL, EMOTION_THRESHOLD, USE_ML_EMOTION

# Try to import ML dependencies
try:
    from transformers import pipeline
    import torch
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: transformers not installed. Using keyword-based emotion detection.")

class EmotionAnalyzer:
    """
    Emotion analyzer with ML model and keyword fallback
    """
    
    def __init__(self, use_ml=USE_ML_EMOTION):
        """
        Initialize emotion analyzer
        
        Args:
            use_ml (bool): Whether to use ML model (if available)
        """
        self.ml_available = ML_AVAILABLE and use_ml
        self.classifier = None
        
        if self.ml_available:
            try:
                device = 0 if torch.cuda.is_available() else -1
                self.classifier = pipeline(
                    "text-classification",
                    model=EMOTION_MODEL,
                    top_k=None,
                    device=device
                )
                print(f"✅ Loaded ML emotion model: {EMOTION_MODEL}")
            except Exception as e:
                print(f"⚠️  Failed to load ML model: {e}")
                print("   Falling back to keyword-based detection")
                self.ml_available = False
        
        # Load keyword dictionary for fallback
        self.keywords = self._load_keywords()
    
    def analyze(self, text):
        """
        Analyze emotion with primary and secondary emotions
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Emotion analysis results
        """
        if not text or not text.strip():
            return self._neutral_response()
        
        if self.ml_available and self.classifier:
            return self._ml_analyze(text)
        else:
            return self._keyword_analyze(text)
    
    def _ml_analyze(self, text):
        """
        ML-based emotion analysis using DistilRoBERTa
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Emotion scores and labels
        """
        try:
            # Truncate very long text to avoid token limits (512 tokens)
            if len(text) > 2000:  # Rough character estimate
                text = text[:2000]
            
            results = self.classifier(text)[0]
            
            # Sort by score
            results = sorted(results, key=lambda x: x['score'], reverse=True)
            
            primary_emotion = results[0]['label']
            primary_score = results[0]['score']
            
            # Get secondary emotion if score is significant
            secondary_emotion = None
            secondary_score = 0
            
            if len(results) > 1 and results[1]['score'] > EMOTION_THRESHOLD:
                secondary_emotion = results[1]['label']
                secondary_score = results[1]['score']
            
            return {
                "primary_emotion": primary_emotion,
                "primary_score": round(primary_score, 3),
                "secondary_emotion": secondary_emotion,
                "secondary_score": round(secondary_score, 3) if secondary_emotion else 0,
                "all_scores": {r['label']: round(r['score'], 3) for r in results[:5]},  # Top 5
                "method": "ml"
            }
        except Exception as e:
            print(f"⚠️  ML analysis failed: {e}. Using keyword fallback.")
            return self._keyword_analyze(text)
    
    def _keyword_analyze(self, text):
        """
        Fallback keyword-based analysis
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Emotion scores and labels
        """
        text_lower = text.lower()
        emotion_scores = {}
        
        # Count keyword matches for each emotion
        for emotion, words in self.keywords.items():
            score = sum(1 for word in words if word in text_lower)
            emotion_scores[emotion] = score
        
        # If no emotions detected, return neutral
        if not any(emotion_scores.values()):
            return self._neutral_response()
        
        # Sort emotions by score
        sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate normalized scores
        total_matches = sum(emotion_scores.values())
        normalized_scores = {
            emotion: round(score / total_matches, 3) if total_matches > 0 else 0
            for emotion, score in emotion_scores.items()
        }
        
        primary_emotion = sorted_emotions[0][0]
        secondary_emotion = sorted_emotions[1][0] if len(sorted_emotions) > 1 and sorted_emotions[1][1] > 0 else None
        
        return {
            "primary_emotion": primary_emotion,
            "primary_score": normalized_scores.get(primary_emotion, 0),
            "secondary_emotion": secondary_emotion,
            "secondary_score": normalized_scores.get(secondary_emotion, 0) if secondary_emotion else 0,
            "all_scores": normalized_scores,
            "method": "keyword"
        }
    
    def _neutral_response(self):
        """Return neutral emotion response"""
        return {
            "primary_emotion": "neutral",
            "primary_score": 1.0,
            "secondary_emotion": None,
            "secondary_score": 0,
            "all_scores": {"neutral": 1.0},
            "method": "default"
        }
    
    def _load_keywords(self):
        """
        Load enhanced keyword dictionary for fallback
        
        Returns:
            dict: Emotion keywords mapping
        """
        return {
            "joy": [
                "happy", "happiness", "joy", "joyful", "love", "loved", "loving",
                "smile", "smiling", "laugh", "laughing", "laughter", "celebrate",
                "celebration", "wonderful", "delight", "delightful", "cheerful",
                "excited", "excitement", "pleased", "glad", "grateful", "fun"
            ],
            "sadness": [
                "sad", "sadness", "cry", "crying", "tears", "lonely", "alone",
                "sorrow", "sorrowful", "grief", "grieving", "despair", "miserable",
                "depressed", "depression", "unhappy", "tragic", "tragedy", "heartbreak",
                "heartbroken", "gloomy", "melancholy", "mourn", "mourning"
            ],
            "anger": [
                "angry", "anger", "mad", "rage", "furious", "fury", "hate",
                "hatred", "hostile", "violence", "violent", "fight", "fighting",
                "scream", "screaming", "yell", "yelling", "frustrated", "frustration",
                "annoyed", "irritated", "outrage", "enraged"
            ],
            "fear": [
                "fear", "afraid", "scared", "frightened", "terrified", "terror",
                "panic", "panicked", "dread", "dreading", "horror", "horrified",
                "anxious", "anxiety", "nervous", "worried", "worry", "threat",
                "threatening", "danger", "dangerous", "dark", "darkness", "ghost"
            ],
            "surprise": [
                "surprise", "surprised", "surprising", "shock", "shocked", "shocking",
                "sudden", "suddenly", "unexpected", "unexpectedly", "amazed",
                "amazing", "astonished", "astonishing", "startled", "wow"
            ],
            "disgust": [
                "disgusting", "disgust", "disgusted", "revolting", "repulsive",
                "sick", "sickening", "awful", "terrible", "horrible", "gross",
                "nasty", "vile", "repugnant"
            ],
            "neutral": [
                "said", "say", "says", "walked", "walk", "went", "go", "goes",
                "looked", "look", "looks", "saw", "see", "sees", "came", "come",
                "did", "do", "does", "was", "were", "is", "are"
            ]
        }

# Global singleton instance
_analyzer_instance = None

def get_analyzer():
    """
    Get or create singleton analyzer instance
    
    Returns:
        EmotionAnalyzer: Analyzer instance
    """
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = EmotionAnalyzer()
    return _analyzer_instance

def analyze_emotion(text):
    """
    Convenience function for emotion analysis
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Emotion analysis results
    """
    analyzer = get_analyzer()
    return analyzer.analyze(text)