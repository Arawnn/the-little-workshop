import { setRobotState } from "./scene";
import { isRobotState } from "./trace";


const eventList = document.querySelector('#trace');  
if (!eventList) {
  throw new Error("Event list does not exist in DOM.");
  
}

const btnPullLever = document.querySelector<HTMLButtonElement>('#pull-lever');
if (!btnPullLever) {
  throw new Error("Pull the lever button not detected.")
}

const state = 'repairing'
if (!isRobotState(state)) {
  throw new Error('Invalid state value for the Robot.')
}
setRobotState(state)

const pullLever = async () => {
  btnPullLever.disabled = true

  try {
    const response = await fetch("/api/lever", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({}),
    });

    if (!response.ok) {
      console.error(response.status)
    }  
  } catch(error) {
    console.error('Request failed:', error)
  } finally {
    btnPullLever.disabled = false
  }  
}

btnPullLever.addEventListener('click', pullLever)
const eventSource = new EventSource('/api/events');


eventSource.onmessage = (e) => {
  const newElement = document.createElement('li')
  
  const result = JSON.parse(e.data)
  
  let reason = ''
  if (result.reason) {
    reason = `: ${result.reason}`
  }
  
  newElement.textContent = `${result.before} → ${result.after} (${result.outcome}${reason})`;
  
  eventList.appendChild(newElement);
}
