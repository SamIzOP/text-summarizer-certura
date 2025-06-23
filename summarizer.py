from flask import Flask, render_template, request, jsonify
import spacy
from collections import Counter
import re
import os

app = Flask(__name__)

class TextSummarizer:
    def __init__(self):
        """Initialize the text summarizer with spaCy model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Please install the English model: python -m spacy download en_core_web_sm")
            raise
    
    def preprocess_text(self, text):
        """Clean and preprocess the input text"""
        text = re.sub(r'\s+', ' ', text.strip())
        return text
    
    def extract_sentences(self, text):
        """Extract sentences from text using spaCy"""
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]
        return sentences
    
    def calculate_word_frequencies(self, text):
        """Calculate word frequencies, excluding stop words"""
        doc = self.nlp(text.lower())
        word_freq = Counter()
        
        for token in doc:
            if (not token.is_stop and 
                not token.is_punct and 
                not token.is_space and 
                len(token.text) > 2):
                word_freq[token.lemma_] += 1
        
        # Normalize frequencies
        max_freq = max(word_freq.values()) if word_freq else 1
        for word in word_freq:
            word_freq[word] = word_freq[word] / max_freq
        
        return word_freq
    
    def score_sentences(self, sentences, word_freq):
        """Score sentences based on word frequencies"""
        sentence_scores = {}
        
        for sentence in sentences:
            doc = self.nlp(sentence.lower())
            score = 0
            word_count = 0
            
            for token in doc:
                if token.lemma_ in word_freq:
                    score += word_freq[token.lemma_]
                    word_count += 1
            
            if word_count > 0:
                sentence_scores[sentence] = score / word_count
            else:
                sentence_scores[sentence] = 0
        
        return sentence_scores
    
    def summarize_text(self, text, num_sentences=3):
        """Summarize text by extracting the most important sentences"""
        if not text.strip():
            return "No text provided for summarization."
        
        clean_text = self.preprocess_text(text)
        sentences = self.extract_sentences(clean_text)
        
        if len(sentences) <= num_sentences:
            return " ".join(sentences)
        
        word_freq = self.calculate_word_frequencies(clean_text)
        sentence_scores = self.score_sentences(sentences, word_freq)
        
        # Select top sentences
        top_sentences = sorted(sentence_scores.items(), 
                              key=lambda x: x[1], 
                              reverse=True)[:num_sentences]
        
        # Maintain original order
        summary_sentences = []
        for sentence in sentences:
            if any(sentence == sent[0] for sent in top_sentences):
                summary_sentences.append(sentence)
        
        return " ".join(summary_sentences)

# Initialize the summarizer
try:
    summarizer = TextSummarizer()
    print("✅ Text summarizer initialized successfully!")
except Exception as e:
    print(f"❌ Error initializing summarizer: {e}")
    summarizer = None

# Example texts
EXAMPLE_TEXTS = {
    'ai': """Artificial intelligence (AI) is transforming the world in unprecedented ways. Machine learning algorithms are becoming more sophisticated and can now perform tasks that were once thought to be exclusively human. Deep learning, a subset of machine learning, uses neural networks with multiple layers to process complex data patterns. These networks can recognize images, understand natural language, and even generate creative content. The applications of AI are vast and growing rapidly across industries. In healthcare, AI helps diagnose diseases and discover new treatments. In transportation, autonomous vehicles use AI to navigate safely. In finance, AI algorithms detect fraud and make investment decisions. However, the rapid advancement of AI also raises important ethical questions about privacy, job displacement, and the need for responsible development. As AI continues to evolve, it will be crucial to balance innovation with careful consideration of its societal impact.""",
    
    'climate': """Climate change represents one of the most pressing challenges of our time, with far-reaching consequences for ecosystems, human societies, and the global economy. Rising global temperatures, primarily driven by greenhouse gas emissions from human activities, are causing dramatic shifts in weather patterns worldwide. These changes manifest as more frequent and severe extreme weather events, including hurricanes, droughts, floods, and heatwaves. The melting of polar ice caps and glaciers contributes to rising sea levels, threatening coastal communities and island nations. Ocean acidification, caused by increased CO2 absorption, endangers marine ecosystems and fisheries. Agricultural systems face disruption from changing precipitation patterns and temperature fluctuations, potentially affecting food security globally. The transition to renewable energy sources, implementation of carbon pricing mechanisms, and international cooperation through agreements like the Paris Climate Accord are essential steps toward mitigating these effects. Individual actions, corporate responsibility, and government policies must work together to address this complex challenge before irreversible tipping points are reached.""",
    
    'space': """Space exploration has entered a new golden age, driven by both government agencies and private companies pushing the boundaries of human knowledge and capability. NASA's Artemis program aims to return humans to the Moon by 2026, establishing a sustainable lunar presence that will serve as a stepping stone to Mars. Private companies like SpaceX have revolutionized space travel with reusable rockets, dramatically reducing launch costs and making space more accessible. The International Space Station continues to serve as a vital platform for scientific research, international cooperation, and technology development. Robotic missions to Mars, including rovers like Perseverance, are searching for signs of ancient life and preparing for future human missions. The James Webb Space Telescope has opened new windows into the early universe, discovering exoplanets and providing unprecedented insights into cosmic evolution. Commercial space tourism is becoming reality, with companies offering suborbital flights to civilian passengers. Meanwhile, space-based technologies continue to benefit life on Earth through satellite communications, GPS navigation, weather monitoring, and Earth observation systems. As we venture further into the cosmos, space exploration promises to unite humanity in pursuit of knowledge and survival beyond our home planet."""
}

@app.route('/')
def index():
    """Main page route"""
    return render_template('index.html')

@app.route('/api/summarize', methods=['POST'])
def api_summarize():
    """API endpoint for text summarization"""
    try:
        if not summarizer:
            return jsonify({
                'error': 'Text summarizer not available. Please ensure spaCy is properly installed.'
            }), 500
        
        data = request.get_json()
        text = data.get('text', '').strip()
        num_sentences = int(data.get('num_sentences', 3))
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if num_sentences < 1 or num_sentences > 10:
            return jsonify({'error': 'Number of sentences must be between 1 and 10'}), 400
        
        # Generate summary
        summary = summarizer.summarize_text(text, num_sentences)
        
        # Calculate statistics
        original_words = len(text.split())
        summary_words = len(summary.split())
        original_sentences = len(summarizer.extract_sentences(text))
        compression_ratio = round((1 - summary_words / original_words) * 100) if original_words > 0 else 0
        
        return jsonify({
            'summary': summary,
            'stats': {
                'original_words': original_words,
                'summary_words': summary_words,
                'original_sentences': original_sentences,
                'summary_sentences': min(num_sentences, original_sentences),
                'compression_ratio': compression_ratio
            }
        })
    
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/examples/<example_type>')
def get_example(example_type):
    """Get example text"""
    if example_type in EXAMPLE_TEXTS:
        return jsonify({'text': EXAMPLE_TEXTS[example_type]})
    else:
        return jsonify({'error': 'Example not found'}), 404

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'summarizer_available': summarizer is not None
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
