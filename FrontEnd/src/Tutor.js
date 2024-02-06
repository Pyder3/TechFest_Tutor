import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Tutor = () => {
  const [question, setQuestion] = useState('');
  const [userCode, setUserCode] = useState('');
  const [feedback, setFeedback] = useState('');
  const [correctCode, setCorrectCode] = useState(''); // State to store the correct code
  const [test_case, setTest_case] = useState(''); // State to store the test case
  const [time_complexity, setTime_complexity] = useState(''); // State to store the time complexity

  useEffect(() => {
    fetchQuestion();
  }, []);

  const fetchQuestion = async () => {
    const postData = {
      difficulty: "easy", // Example data field
      // Include other fields as needed
    };
    try {
      const response = await axios.post('http://127.0.0.1:5000/generate-question', postData);
      setQuestion(response.data.question);
      setTest_case(response.data.test_cases[0]);
      setTime_complexity(response.data.time_complexity);
      // Reset states
      setUserCode('');
      setFeedback('');
      setCorrectCode(''); // Reset the correct code when fetching a new question
    } catch (error) {
      console.error('Error fetching question:', error);
    }
  };

  const handleSubmit = async () => {
    try {

      const response = await axios.post('http://127.0.0.1:5000/submit_code', { code: userCode, test_case: test_case, time_complexity: time_complexity, question: question});
      // Assuming the response includes fields for correctness and a hint if needed
      if (response.data.is_code_correct=="True" && response.data.is_optimal_code=="True") {
        setFeedback("Correct");
      } else if (response.data.is_code_correct=="True" && response.data.is_optimal_code=="False") {
        setFeedback(response.data.hint); // Display the hint from the backend
      }
      else if (response.data.is_code_correct=="False") {
        setFeedback("Incorrect");
      }
      setCorrectCode(''); // Clear the correct code display if previously shown
    } catch (error) {
      console.error('Error submitting code:', error);
    }
  };

  const handleQuit = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/generate_code', { question: question});
      setCorrectCode(response.data.code); // Display the correct code
      setFeedback(''); // Clear any existing feedback
    } catch (error) {
      console.error('Error getting answer:', error);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ marginBottom: '20px' }}>
        <div>Question: {question}</div>
        <textarea
          rows="10"
          cols="50"
          value={userCode}
          onChange={(e) => setUserCode(e.target.value)}
          style={{ marginTop: '10px', padding: '10px', width: '100%' }}
        />
      </div>
      <button onClick={handleSubmit} style={{ marginRight: '10px' }}>Submit</button>
      <button onClick={fetchQuestion} style={{ marginRight: '10px' }}>Next Question</button>
      <button onClick={handleQuit}>Quit</button>
      {feedback && <div style={{ marginTop: '20px' }}>{feedback}</div>}
      {correctCode && <div style={{ marginTop: '20px' }}>Correct Code: <pre>{correctCode}</pre></div>}
    </div>
  );
};

export default Tutor;
