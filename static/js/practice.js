let currentQuestion = 0;
let totalQuestions = 0;
let markedForReview = {};
let answers = {};

function startTimer(duration) {
    let timer = duration;
    const timerDisplay = document.getElementById('timer');
    if (!timerDisplay) {
        console.error('Timer element not found');
        return;
    }
    
    const interval = setInterval(() => {
        let minutes = Math.floor(timer / 60);
        let seconds = timer % 60;
        seconds = seconds < 10 ? '0' + seconds : seconds;
        timerDisplay.textContent = `${minutes}:${seconds}`;
        
        timer--;
        if (timer < 0) {
            clearInterval(interval);
            alert('Time is up!');
            submitTest();
        }
    }, 1000);
}

function loadQuestion(qid) {
    console.log(`Loading question ${qid}`);  // Debugging
    fetch('/practice', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ next_question: qid }),
    })
    .then(response => {
        console.log('Fetch response received:', response);  // Debugging
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Question data received:', data);  // Debugging
        if (data.error) {
            alert(data.error);
            window.location.href = '/login';
            return;
        }
        if (data.redirect) {
            window.location.href = data.redirect;
            return;
        }
        
        currentQuestion = data.qid;
        totalQuestions = data.total_questions;
        markedForReview[currentQuestion] = data.marked;
        answers[currentQuestion] = data.answer;
        
        // Update section title
        const sectionTitleElement = document.getElementById('section-title');
        const modalSectionTitleElement = document.getElementById('modal-section-title');
        if (sectionTitleElement) {
            sectionTitleElement.textContent = data.section_name;
        } else {
            console.error('Section title element not found');
        }
        if (modalSectionTitleElement) {
            modalSectionTitleElement.textContent = data.section_name.replace('Section', 'Section ').replace('Module', 'Module ');
        } else {
            console.error('Modal section title element not found');
        }

        // Show/hide Desmos calculator button based on section (Math sections are 2 and 4)
        const desmosButton = document.getElementById('desmos-calculator');
        if (desmosButton) {
            if (data.section_name.includes('Math')) {
                desmosButton.classList.remove('hidden');
            } else {
                desmosButton.classList.add('hidden');
            }
        } else {
            console.error('Desmos calculator button not found');
        }
        
        // Update passage
        const passageElement = document.getElementById('passage');
        if (passageElement) {
            passageElement.innerHTML = data.question.passage || '';
        } else {
            console.error('Passage element not found');
        }
        
        // Update passage image
        const passageImageElement = document.getElementById('passage-image');
        if (passageImageElement) {
            console.log(`Checking passage image: image=${data.question.image}, includes 'verbal'=${data.question.image && data.question.image.includes('verbal')}`);  // Debugging
            if (data.question.image && data.question.image.includes('verbal')) {
                passageImageElement.innerHTML = `<img src="/static/${data.question.image}" alt="Passage Image" class="max-w-full h-auto">`;
                console.log(`Set passage image to /static/${data.question.image}`);  // Debugging
            } else {
                passageImageElement.innerHTML = '';
                console.log('Cleared passage image');  // Debugging
            }
        } else {
            console.error('Passage image element not found');
        }
        
        // Update question
        const questionNumberElement = document.getElementById('question-number');
        const questionTextElement = document.getElementById('question-text');
        if (questionNumberElement) {
            questionNumberElement.textContent = `${currentQuestion + 1}`;
        } else {
            console.error('Question number element not found');
        }
        if (questionTextElement) {
            questionTextElement.textContent = data.question.question || 'No question text available';
        } else {
            console.error('Question text element not found');
        }
        
        // Update question image
        const questionImageElement = document.getElementById('question-image');
        if (questionImageElement) {
            console.log(`Checking question image: image=${data.question.image}, includes 'verbal'=${data.question.image && !data.question.image.includes('verbal')}`);  // Debugging
            if (data.question.image && !data.question.image.includes('verbal')) {
                questionImageElement.innerHTML = `<img src="/static/${data.question.image}" alt="Question Image" class="max-w-full h-auto">`;
                console.log(`Set question image to /static/${data.question.image}`);  // Debugging
            } else {
                questionImageElement.innerHTML = '';
                console.log('Cleared question image');  // Debugging
            }
        } else {
            console.error('Question image element not found');
        }
        
        // Update equation
        const equationElement = document.getElementById('question-equation');
        if (equationElement) {
            if (data.question.equation) {
                equationElement.innerHTML = `\\[${data.question.equation}\\]`;
                // Trigger MathJax to render the equation
                if (typeof MathJax !== 'undefined') {
                    MathJax.typesetPromise([equationElement]).catch(err => {
                        console.error('MathJax error:', err);
                        equationElement.innerHTML = `<p>Error rendering equation: ${data.question.equation}</p>`;
                    });
                } else {
                    console.error('MathJax not loaded');
                    equationElement.innerHTML = `<p>Equation: ${data.question.equation} (Math rendering unavailable)</p>`;
                }
            } else {
                equationElement.innerHTML = '';
            }
        } else {
            console.error('Question equation element not found');
        }
        
        // Update options
        const optionsDiv = document.getElementById('options');
        if (optionsDiv) {
            optionsDiv.innerHTML = '';
            if (data.question.options && Array.isArray(data.question.options)) {
                data.question.options.forEach((option, index) => {
                    const label = document.createElement('label');
                    label.className = 'block mb-2';
                    const input = document.createElement('input');
                    input.type = 'radio';
                    input.name = 'answer';
                    input.value = option;
                    input.className = 'mr-2';
                    if (data.answer === option) {
                        input.checked = true;
                    }
                    label.appendChild(input);
                    label.appendChild(document.createTextNode(option));
                    optionsDiv.appendChild(label);
                });
            } else {
                console.error('No options available for this question:', data.question);
                optionsDiv.innerHTML = '<p>No options available.</p>';
            }
        } else {
            console.error('Options element not found');
        }
        
        // Update progress button
        const questionProgressElement = document.getElementById('question-progress');
        if (questionProgressElement) {
            questionProgressElement.textContent = `Question ${currentQuestion + 1} of ${totalQuestions}`;
        } else {
            console.error('Question progress element not found');
        }
        
        // Update mark for review button
        const markButton = document.getElementById('mark-for-review');
        if (markButton) {
            markButton.textContent = markedForReview[currentQuestion] ? 'Unmark' : 'Mark for Review';
        } else {
            console.error('Mark for review button not found');
        }
        
        // Update back button state
        const backButton = document.getElementById('back-button');
        if (backButton) {
            backButton.disabled = currentQuestion === 0;
            console.log(`Back button state: disabled=${backButton.disabled}, currentQuestion=${currentQuestion}`);  // Debugging
        } else {
            console.error('Back button not found');
        }
    })
    .catch(error => {
        console.error('Error loading question:', error);
        alert('An error occurred while loading the question.');
    });
}

function saveAnswer() {
    const form = document.getElementById('practice-form');
    if (!form) {
        console.error('Practice form not found');
        return;
    }
    const formData = new FormData(form);
    const answer = formData.get('answer');
    
    fetch('/practice', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ current_question: currentQuestion, answer: answer }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            window.location.href = '/login';
            return;
        }
        answers[currentQuestion] = data.answer;
    })
    .catch(error => {
        console.error('Error saving answer:', error);
        alert('An error occurred while saving the answer.');
    });
}

function submitTest() {
    fetch('/practice', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ next_question: totalQuestions }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            window.location.href = '/login';
            return;
        }
        if (data.redirect) {
            window.location.href = data.redirect;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while submitting the test.');
    });
}

function updateQuestionStatus() {
    const grid = document.getElementById('question-status-grid');
    if (!grid) {
        console.error('Question status grid not found');
        return;
    }
    grid.innerHTML = '';
    
    for (let i = 0; i < totalQuestions; i++) {
        const button = document.createElement('button');
        button.textContent = i + 1;
        button.className = 'w-10 h-10 rounded-lg';
        
        if (markedForReview[i]) {
            button.classList.add('bg-yellow-200');
        } else if (answers[i]) {
            button.classList.add('bg-green-200');
        } else {
            button.classList.add('bg-pink-200');
        }
        
        button.addEventListener('click', () => {
            console.log(`Navigating to question ${i} via status grid`);  // Debugging
            saveAnswer();
            currentQuestion = i;  // Update currentQuestion locally
            loadQuestion(i);
            const modal = document.getElementById('question-status-modal');
            if (modal) {
                modal.classList.add('hidden');
            }
        });
        
        grid.appendChild(button);
    }
}

document.getElementById('next-button').addEventListener('click', () => {
    console.log(`Next button clicked: currentQuestion=${currentQuestion}, totalQuestions=${totalQuestions}`);
    saveAnswer();

    if (currentQuestion < totalQuestions - 1) {
        currentQuestion += 1;
        loadQuestion(currentQuestion);
    } else {
        // Show confirmation modal
        const modal = document.getElementById('submit-confirmation-modal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }
});

document.getElementById('confirm-submit').addEventListener('click', () => {
    const modal = document.getElementById('submit-confirmation-modal');
    if (modal) modal.classList.add('hidden');
    submitTest();  // Actually submit
});

document.getElementById('cancel-submit').addEventListener('click', () => {
    const modal = document.getElementById('submit-confirmation-modal');
    if (modal) modal.classList.add('hidden');
});

document.getElementById('back-button').addEventListener('click', () => {
    console.log(`Back button clicked: currentQuestion=${currentQuestion}`);  // Debugging
    if (currentQuestion > 0) {
        saveAnswer();
        currentQuestion -= 1;  // Decrement locally
        loadQuestion(currentQuestion);
    } else {
        console.log('Back button disabled: already on first question');
    }
});

document.getElementById('mark-for-review').addEventListener('click', () => {
    const markButton = document.getElementById('mark-for-review');
    if (!markButton) {
        console.error('Mark for review button not found');
        return;
    }

    // Toggle the marked state and update button text immediately
    markedForReview[currentQuestion] = !markedForReview[currentQuestion];
    markButton.textContent = markedForReview[currentQuestion] ? 'Unmark' : 'Mark for Review';

    fetch('/practice', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ current_question: currentQuestion, mark_for_review: markedForReview[currentQuestion] }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            window.location.href = '/login';
            return;
        }
        updateQuestionStatus();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while marking the question.');
        // Revert the button text if the request fails
        markedForReview[currentQuestion] = !markedForReview[currentQuestion];
        markButton.textContent = markedForReview[currentQuestion] ? 'Unmark' : 'Mark for Review';
    });
});

// document.getElementById('annotate').addEventListener('click', () => {
//     alert('Annotate feature not implemented.');
// });

document.getElementById('question-progress').addEventListener('click', () => {
    updateQuestionStatus();
    const modal = document.getElementById('question-status-modal');
    if (modal) {
        modal.classList.remove('hidden');
    }
});

document.getElementById('close-modal').addEventListener('click', () => {
    const modal = document.getElementById('question-status-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
});

// Desmos Calculator Modal Event Listeners
document.getElementById('desmos-calculator').addEventListener('click', () => {
    console.log('Desmos calculator button clicked');  // Debugging
    const desmosModal = document.getElementById('desmos-calculator-modal');
    if (desmosModal) {
        desmosModal.classList.remove('hidden');
    }
});

document.getElementById('close-desmos-modal').addEventListener('click', () => {
    console.log('Close Desmos modal clicked');  // Debugging
    const desmosModal = document.getElementById('desmos-calculator-modal');
    if (desmosModal) {
        desmosModal.classList.add('hidden');
    }
});