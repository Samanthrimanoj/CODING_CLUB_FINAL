// Quiz functionality for GMU Coding Club

const quizQuestions = [
    {
        question: "What does HTML stand for?",
        options: [
            "Hyper Text Markup Language",
            "High Tech Modern Language",
            "Hyper Transfer Markup Language",
            "Home Tool Markup Language"
        ],
        correct: 0,
        explanation: "HTML stands for Hyper Text Markup Language, which is the standard markup language for creating web pages."
    },
    {
        question: "Which of the following is NOT a JavaScript data type?",
        options: [
            "string",
            "boolean",
            "integer",
            "character"
        ],
        correct: 3,
        explanation: "JavaScript has number (not integer), string, boolean, null, undefined, symbol, and bigint data types. Character is not a separate data type."
    }
];

let currentQuestion = 0;
let score = 0;

function startQuiz() {
    document.getElementById('start-btn').style.display = 'none';
    showQuestion();
}

function showQuestion() {
    const container = document.getElementById('quiz-container');
    const question = quizQuestions[currentQuestion];
    
    container.innerHTML = `
        <div class="quiz-question">
            <h4>Question ${currentQuestion + 1} of ${quizQuestions.length}</h4>
            <p>${question.question}</p>
        </div>
        <div class="quiz-options">
            ${question.options.map((option, index) => `
                <div class="quiz-option" onclick="selectOption(${index})">
                    ${String.fromCharCode(65 + index)}) ${option}
                </div>
            `).join('')}
        </div>
        <div id="explanation" class="mt-3" style="display: none;"></div>
    `;
}

function selectOption(selectedIndex) {
    const options = document.querySelectorAll('.quiz-option');
    const question = quizQuestions[currentQuestion];
    
    options.forEach((option, index) => {
        option.classList.remove('selected', 'correct', 'incorrect');
        
        if (index === question.correct) {
            option.classList.add('correct');
        }
        
        if (index === selectedIndex) {
            option.classList.add('selected');
            if (index !== question.correct) {
                option.classList.add('incorrect');
            }
        }
    });
    
    // Show explanation
    const explanationDiv = document.getElementById('explanation');
    explanationDiv.innerHTML = `<div class="alert alert-info">${question.explanation}</div>`;
    explanationDiv.style.display = 'block';
    
    // Move to next question after delay
    setTimeout(() => {
        currentQuestion++;
        if (currentQuestion < quizQuestions.length) {
            showQuestion();
        } else {
            showResults();
        }
    }, 2000);
}

function showResults() {
    const container = document.getElementById('quiz-container');
    container.innerHTML = `
        <div class="text-center">
            <h3>Quiz Completed!</h3>
            <p>Your score: ${score} out of ${quizQuestions.length}</p>
            <button class="btn btn-primary" onclick="location.reload()">Restart Quiz</button>
        </div>
    `;
}

// Add CSS for quiz
const quizStyles = `
    .quiz-question {
        font-size: 1.2rem;
        margin-bottom: 1.5rem;
    }
    
    .quiz-option {
        padding: 15px;
        margin: 10px 0;
        border: 2px solid #e9ecef;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .quiz-option:hover {
        border-color: #006633;
        background-color: #f8f9fa;
    }
    
    .quiz-option.selected {
        border-color: #006633;
        background-color: #e8f5e8;
    }
    
    .quiz-option.correct {
        border-color: #28a745;
        background-color: #d4edda;
    }
    
    .quiz-option.incorrect {
        border-color: #dc3545;
        background-color: #f8d7da;
    }
`;

const styleSheet = document.createElement('style');
styleSheet.innerText = quizStyles;
document.head.appendChild(styleSheet);

// Initialize quiz
document.getElementById('start-btn').addEventListener('click', startQuiz);