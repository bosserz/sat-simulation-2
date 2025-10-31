let currentQuestion = 0;
let totalQuestions = 0;
let markedForReview = {};
let answers = {};

// timer state
window.timerInterval = null;
window.timerStarted = false;   // has the timer actually begun ticking?
window.timerArmed = false;     // do we have a duration ready to start?
window.timerDuration = null;   // seconds for next section

function startTimer(duration) {
    let timer = duration;
    const timerDisplay = document.getElementById('timer');
    if (!timerDisplay) return;

    clearInterval(window.timerInterval); // Make sure only one interval runs

    window.timerInterval = setInterval(() => {
        const minutes = Math.floor(timer / 60);
        const seconds = timer % 60;
        timerDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

        timer--;
        if (timer < 0) {
            clearInterval(window.timerInterval);
            alert('Time is up!');
            submitTest();
        }
    }, 1000);
}

// function startTimer(duration) {
//   let timer = duration;
//   const timerDisplay = document.getElementById('timer');
//   if (!timerDisplay) return;

//   clearInterval(window.timerInterval);
//   window.timerStarted = true;
//   window.timerArmed = false;
//   window.timerDuration = duration;

//   window.timerInterval = setInterval(() => {
//     const minutes = Math.floor(timer / 60);
//     const seconds = timer % 60;
//     timerDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

//     timer--;
//     if (timer < 0) {
//       clearInterval(window.timerInterval);
//       window.timerStarted = false;
//       alert('Time is up!');
//       submitTest();
//     }
//   }, 1000);
// }

function armTimer(duration) {
  // prepare the timer but do not start it yet
  window.timerDuration = duration;
  window.timerArmed = true;
  window.timerStarted = false;
  clearInterval(window.timerInterval);
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

        const referenceFormulaButton = document.getElementById('reference-formula');
        if (referenceFormulaButton) {
            if (data.section_name.includes('Math')) {
                referenceFormulaButton.classList.remove('hidden');
            } else {
                referenceFormulaButton.classList.add('hidden');
            }
        }
        
        // Update passage
        const passageElement = document.getElementById('passage');
        const passageParent = passageElement ? passageElement.parentElement : null;
        const questionContainer = document.getElementById('question-container');

        if (passageElement && passageParent && questionContainer) {
            const passageHTML = data.question.passage || '';
            const options = Array.isArray(data.question.options) ? data.question.options : [];
            const noPassage = !passageHTML || passageHTML.trim() === '';
            const hasOptions = options.length > 0;
            const noOptions = options.length === 0;

            // 🔹 Case 1: Passage empty but has options → hide passage + expand question area
            if (noPassage && hasOptions) {
                passageParent.style.display = 'none';
                questionContainer.classList.remove('w-1/2');
                questionContainer.classList.add('w-3/5');
                questionContainer.classList.add('mx-auto');
            } 
            // 🔹 Case 2: No options (student-produced response) → show special directions
            else if (noOptions) {
                passageParent.style.display = 'block';
                questionContainer.classList.remove('w-full');
                questionContainer.classList.add('w-1/2');
                passageElement.innerHTML = `
                    <h3 class="font-bold">Student-produced response directions</h3>
                    <ul class="list-disc list-inside text-small mb-4">
                        <li>If you find more than one correct answer, enter only one answer.</li>
                        <li>You can enter up to 5 characters for a positive answer and up to 6 characters (including the negative sign) for a negative answer.</li>
                        <li>If your answer is a fraction that doesn't fit in the provided space, enter the decimal equivalent.</li>
                        <li>If your answer is a decimal that doesn't fit in the provided space, enter it by truncating or rounding at the fourth digit.</li>
                        <li>If your answer is a mixed number (such as 3½), enter it as an improper fraction (7/2) or its decimal equivalent (3.5).</li>
                        <li>Don't enter symbols such as a percent sign, comma, or dollar sign.</li>
                    </ul>
                    <h4 class="font-bold text-center">Examples</h4>
                    <table border="1" cellspacing="0" cellpadding="8" class="text-center text-small mx-auto explained-table">
                        <tr>
                            <th>Answer</th>
                            <th>Acceptable ways to enter answer</th>
                            <th>Unacceptable: will NOT receive credit</th>
                        </tr>
                        <tr>
                            <td><b>3.5</b></td>
                            <td>3.5<br>3.50<br>7/2</td>
                            <td>3 1/2<br>3  1/2</td>
                        </tr>
                        <tr>
                            <td><b>2/3</b></td>
                            <td>2/3<br>.6666<br>.6667<br>0.666<br>0.667</td>
                            <td>0.66<br>.66<br>0.67<br>.67</td>
                        </tr>
                        <tr>
                            <td><b>-1/3</b></td>
                            <td>-1/3<br>-.3333<br>-0.333</td>
                            <td>-.33<br>-0.33</td>
                        </tr>
                    </table>
                `;
            } 
            // 🔹 Case 3: Passage exists → show it normally
            else {
                passageParent.style.display = 'block';
                questionContainer.classList.remove('w-full');
                questionContainer.classList.add('w-1/2');
                passageElement.innerHTML = passageHTML;
            }

            // Render MathJax only when passage is not empty and not special directions
            if (!noPassage && hasOptions && typeof MathJax !== 'undefined') {
                MathJax.typesetPromise([passageElement]).catch(err => {
                    console.error('MathJax error:', err);
                });
            }
        } else {
            console.error('Passage or container elements not found');
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
            // questionTextElement.textContent = data.question.question || 'No question text available';
            questionTextElement.innerHTML = data.question.question || 'No question text available';
            if (typeof MathJax !== 'undefined') {
                MathJax.typesetPromise([questionTextElement]).catch(err => {
                    console.error('MathJax error:', err);
                });
            }
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
            if (Array.isArray(data.question.options)) {
            optionsDiv.innerHTML = '';

            if (data.question.options.length === 0) {
            // 🧠 Fill-in-the-blank input box
            const input = document.createElement('input');
            input.type = 'text';
            input.name = 'answer';
            input.className = 'w-full p-2 border border-gray-300 rounded';
            input.value = data.answer || '';

            // ✅ Allow only digits, '/', and '.'
            input.setAttribute('inputmode', 'decimal');           // mobile numeric keyboard
            input.setAttribute('pattern', '[0-9./-]*');            // form validation on submit
            input.setAttribute('title', "Only numbers, '/', and '.' are allowed");

            const allowed = /^[0-9./-]*$/;

            // Block bad keystrokes but allow control keys
            input.addEventListener('keydown', (e) => {
                const ctrlKeys = ['Backspace','Delete','ArrowLeft','ArrowRight','Home','End','Tab','Enter'];
                if (ctrlKeys.includes(e.key) || (e.ctrlKey || e.metaKey)) return;
                if (!/[0-9/.-]/.test(e.key)) e.preventDefault();
            });

            // Clean pasted/IME text
            const sanitize = (el) => { el.value = el.value.replace(/[^0-9./-]/g, ''); };
            input.addEventListener('paste', (e) => {
                e.preventDefault();
                const text = (e.clipboardData || window.clipboardData).getData('text');
                const cleaned = text.replace(/[^0-9./-]/g, '');
                document.execCommand('insertText', false, cleaned);
            });
            input.addEventListener('input', () => {
                if (!allowed.test(input.value)) sanitize(input);
            });

            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                e.preventDefault();
                const nextBtn = document.getElementById('next-button');
                if (nextBtn) nextBtn.click();
                }
            });

            optionsDiv.appendChild(input);
            } else {
                // 🧠 Multiple choice radio options
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

                    const optionSpan = document.createElement('span');
                    optionSpan.innerHTML = option;
                    label.appendChild(input);
                    label.appendChild(optionSpan);
                    optionsDiv.appendChild(label);
                });

                // 🧠 Render math if needed
                if (typeof MathJax !== 'undefined') {
                    MathJax.typesetPromise([optionsDiv]).catch(err => {
                        console.error('MathJax error in options:', err);
                    });
                }
            }
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
        return Promise.resolve();  // return resolved Promise to prevent blocking
    }

    let answer = null;
    const formData = new FormData(form);

    answer = formData.get('answer');

    if (!answer) {
        const textInput = form.querySelector('input[type="text"][name="answer"]');
        if (textInput) {
            answer = textInput.value.trim();
        }
    }

    return fetch('/practice', {
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



// function submitTest() {
//     // stop any running timer as we’re leaving this section
//     clearInterval(window.timerInterval);
//     window.timerStarted = false;
//     window.timerArmed = false;
//     // previous code
//     fetch('/practice', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ next_question: totalQuestions }),
//     })
//     .then(response => response.json())
//     .then(data => {
//         if (data.error) {
//             alert(data.error);
//             window.location.href = '/login';
//             return;
//         }
//         if (data.redirect) {
//             window.location.href = data.redirect;
//         }
//     })
//     .catch(error => {
//         console.error('Error:', error);
//         alert('An error occurred while submitting the test.');
//     });
// }

function submitTest() {
    fetch('/practice', { method: 'POST', headers: { 'Content-Type': 'application/json', }, body: JSON.stringify({ next_question: totalQuestions }), }).then(response => response.json()).then(data => {
        if (data.error) {
            alert(data.error);
            window.location.href = '/login';
            return;
        }
        if (data.redirect) { window.location.href = data.redirect; }
    }).catch(error => {
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
        
        button.addEventListener('click', async () => {
            console.log(`Navigating to question ${i} via status grid`);
            await saveAnswer();
            currentQuestion = i;
            loadQuestion(i);
            const modal = document.getElementById('question-status-modal');
            if (modal) {
                modal.classList.add('hidden');
            }
        });
        
        grid.appendChild(button);
    }
}

function refreshRemainingTime() {
    fetch('/get_remaining_time')
        .then(response => response.json())
        .then(data => {
            if (data.remaining_time !== undefined) {
                clearInterval(window.timerInterval); // Stop current timer
                startTimer(data.remaining_time);     // Restart with fresh time
            }
        })
        .catch(err => {
            console.error('Failed to refresh remaining time:', err);
        });
}

// function refreshRemainingTime() {
//   fetch('/get_remaining_time')
//     .then(response => response.json())
//     .then(data => {
//       if (data.remaining_time !== undefined) {
//         // update our cached duration
//         armTimer(data.remaining_time);

//         // If the timer was already running before (e.g., user tabbed away and back),
//         // resume it. If not started yet (e.g., we are on break), DO NOT start it.
//         const timerDisplay = document.getElementById('timer');
//         if (window.timerStarted && timerDisplay) {
//           startTimer(window.timerDuration);
//         }
//       }
//     })
//     .catch(err => {
//       console.error('Failed to refresh remaining time:', err);
//     });
// }

// function refreshRemainingTime() {
//   fetch('/get_remaining_time')
//     .then(r => r.json())
//     .then(d => {
//       if (d.remaining_time !== undefined) {
//         armTimer(d.remaining_time);  // updates cached duration & clears any stale interval

//         // If we were already running before (tab switch, etc.), resume
//         const timerDisplay = document.getElementById('timer');
//         if (window.timerStarted && timerDisplay) {
//           startTimer(window.timerDuration);
//         }
//       }
//     })
//     .catch(err => console.error('Failed to refresh remaining time:', err));
// }



function updateEndModuleStatus() {
  const grid = document.getElementById('end-module-question-grid');
  const title = document.getElementById('end-modal-section-title');

  if (title) {
    const sectionTitle = document.getElementById('section-title');
    title.textContent = sectionTitle
      ? `Check Your Work: ${sectionTitle.textContent}`
      : "Check Your Work Before Continuing";
  }

  if (!grid) {
    console.error('❌ end-module-question-grid not found');
    return;
  }

  grid.innerHTML = '';

  for (let i = 0; i < totalQuestions; i++) {
    const btn = document.createElement('button');
    btn.textContent = i + 1;
    btn.className = 'w-10 h-10 rounded-lg';

    if (markedForReview[i]) {
      btn.classList.add('bg-yellow-200');
    } else if (answers[i]) {
      btn.classList.add('bg-green-200');
    } else {
      btn.classList.add('bg-pink-200');
    }

    btn.addEventListener('click', async () => {
      await saveAnswer();
      currentQuestion = i;
      loadQuestion(i);
      const modal = document.getElementById('end-of-module-modal');
      if (modal) modal.classList.add('hidden');
    });

    grid.appendChild(btn);
  }
}




// ---------- safe event binding helper ----------
function on(id, event, handler) {
  const el = document.getElementById(id);
  if (!el) {
    console.warn(`Element #${id} not found; skipped binding ${event}`);
    return;
  }
  el.addEventListener(event, handler);
}
// ----------------------------------------------

// Next button
on('next-button', 'click', async () => {
  console.log(`Next clicked: current=${currentQuestion}, total=${totalQuestions}`);

  await saveAnswer();

  totalQuestions = Number(totalQuestions) || 0;

  // Not yet last question → load next
  if (currentQuestion < totalQuestions - 1) {
    currentQuestion++;
    loadQuestion(currentQuestion);
    return;
  }

  // ✅ Last question case
  if (currentQuestion === totalQuestions - 1) {
    console.log("✅ Last question reached, opening End-of-Module modal");
    updateEndModuleStatus();

    const modal = document.getElementById('end-of-module-modal');
    if (modal) {
      modal.classList.remove('hidden');   // remove Tailwind's hidden
      modal.style.display = 'flex';       // ensure it's visible
      console.log("Modal displayed successfully");
    } else {
      console.error("❌ end-of-module-modal not found in DOM");
      alert("End-of-Module modal not found!");
    }
  }
});



// End-of-Module modal controls
on('close-end-modal', 'click', () => {
  const modal = document.getElementById('end-of-module-modal');
  if (modal) modal.classList.add('hidden');
});

on('submit-end-module', 'click', async () => {
  try {
    const modal = document.getElementById('end-of-module-modal');
    if (modal) modal.classList.add('hidden');
    await saveAnswer();
    submitTest();  // move to next section
  } catch (err) {
    console.error('Submit from end-of-module modal failed:', err);
    alert('Failed to submit. Please try again.');
  }
});

// Optional legacy submit-from-review (only if that button exists)
on('submit-from-review', 'click', async () => {
  try {
    const btn = document.getElementById('submit-from-review');
    if (btn) btn.disabled = true;
    await saveAnswer();
    const modal = document.getElementById('question-status-modal');
    if (modal) modal.classList.add('hidden');
    submitTest();
  } catch (e) {
    console.error('Submit from review failed:', e);
    const btn = document.getElementById('submit-from-review');
    if (btn) btn.disabled = false;
    alert('Failed to submit. Please try again.');
  }
});

// Back
on('back-button', 'click', async () => {
  console.log(`Back button clicked: currentQuestion=${currentQuestion}`);
  if (currentQuestion > 0) {
    await saveAnswer();
    currentQuestion -= 1;
    loadQuestion(currentQuestion);
  } else {
    console.log('Back button disabled: already on first question');
  }
});

// Mark for review
on('mark-for-review', 'click', () => {
  const markButton = document.getElementById('mark-for-review');
  if (!markButton) {
    console.error('Mark for review button not found');
    return;
  }

  markedForReview[currentQuestion] = !markedForReview[currentQuestion];
  markButton.textContent = markedForReview[currentQuestion] ? 'Unmark' : 'Mark for Review';

  fetch('/practice', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ current_question: currentQuestion, mark_for_review: markedForReview[currentQuestion] }),
  })
  .then(r => r.json())
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
    // revert
    markedForReview[currentQuestion] = !markedForReview[currentQuestion];
    markButton.textContent = markedForReview[currentQuestion] ? 'Unmark' : 'Mark for Review';
  });
});

// Question progress (Review) modal
on('question-progress', 'click', () => {
  updateQuestionStatus();
  const modal = document.getElementById('question-status-modal');
  if (modal) modal.classList.remove('hidden');
});

on('close-modal', 'click', () => {
  const modal = document.getElementById('question-status-modal');
  if (modal) modal.classList.add('hidden');
});

// Desmos modal
on('desmos-calculator', 'click', () => {
  console.log('Desmos calculator button clicked');
  const m = document.getElementById('desmos-calculator-modal');
  if (m) m.classList.remove('hidden');
});
on('close-desmos-modal', 'click', () => {
  console.log('Close Desmos modal clicked');
  const m = document.getElementById('desmos-calculator-modal');
  if (m) m.classList.add('hidden');
});

// Reference formula modal
on('reference-formula', 'click', () => {
  console.log('Reference formula button clicked');
  const m = document.getElementById('reference-formula-modal');
  if (m) m.classList.remove('hidden');
});
on('close-reference-formula', 'click', () => {
  const m = document.getElementById('reference-formula-modal');
  if (m) m.classList.add('hidden');
});

// Next Section
// on('start-next-section', 'click', async (e) => {
//   e.preventDefault();

//   // Mark that the user explicitly started the next section
//   sessionStorage.setItem('sectionJustStarted', '1');

//   // Notify backend (optional)
//   try {
//     await fetch('/practice/start_timer', { method: 'POST' });
//   } catch (err) {
//     console.warn('Could not notify server timer start:', err);
//   }

//   // Arm duration if provided in data attribute
//   const link = e.currentTarget;
//   const durAttr = parseInt(link.dataset.duration, 10);
//   if (Number.isFinite(durAttr)) armTimer(durAttr);

//   // Redirect to the next section
//   window.location.href = link.href;
// });


// Keep your existing visibilitychange handler as-is


document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        console.log('Tab is active again — refreshing timer');
        refreshRemainingTime();
    }
});

// ---- periodic server sync (prevents drift, handles reloads) ----
// const SYNC_MS = 15000;
// let syncInterval = null;

// function startTimerSyncLoop() {
//   clearInterval(syncInterval);
//   syncInterval = setInterval(() => {
//     refreshRemainingTime();

//     // Safety: if timer should be running but isn't, kick it off.
//     // (e.g., page reload after the section already started)
//     if (!window.timerStarted &&
//         window.timerArmed &&
//         typeof window.timerDuration === 'number' &&
//         window.timerDuration > 0) {
//       startTimer(window.timerDuration);
//     }
//   }, SYNC_MS);
// }


// document.addEventListener('DOMContentLoaded', async () => {
//   // Get authoritative remaining time from server
//   try {
//     const r = await fetch('/get_remaining_time');
//     const d = await r.json();
//     if (d.remaining_time !== undefined) armTimer(d.remaining_time);
//   } catch (e) {
//     console.warn('Failed to fetch remaining time on load:', e);
//   }

//   // Only start if we arrived via Start Next Section click
//   if (sessionStorage.getItem('sectionJustStarted') === '1') {
//     if (typeof window.timerDuration === 'number' && window.timerDuration > 0) {
//       startTimer(window.timerDuration);
//     }
//     sessionStorage.removeItem('sectionJustStarted');
//   }

//   // begin periodic sync
//   startTimerSyncLoop();
// });



// Reference Formula Modal Event Listeners
// document.getElementById('reference-formula').addEventListener('click', () => {
//     console.log('Reference formula button clicked');
//     const refModal = document.getElementById('reference-formula-modal');
//     if (refModal) {
//         refModal.classList.remove('hidden');
//     }
// });

// document.getElementById('close-reference-formula').addEventListener('click', () => {
//     const refModal = document.getElementById('reference-formula-modal');
//     if (refModal) {
//         refModal.classList.add('hidden');
//     }
// });
