const baseUrlOld = "http://127.0.0.1:8000/lab4";
const baseUrl = "https://coe892lab42025g17-eubjf7asb2acbpdx.canadacentral-01.azurewebsites.net/lab4";
let logsVisible = false;

function getMap() {
    fetch(`${baseUrl}/map`)
        .then(response => response.json())
        .then(data => {
            const map = data.data;
            const rows = data.rows;
            const cols = data.cols;

            // Display rows and cols on a separate line
            const mapInfo = `<div><p>Rows: ${rows}<br/>Columns: ${cols}</p><br/>Click the map to view mine serial numbers.</div>`; // Using <br/> for line break

            // Build the map table
            let mapHtml = "<table class='table table-bordered text-center d-flex justify-content-center'>";
            for (let i = 0; i < rows; i++) {
                mapHtml += "<tr>";
                for (let j = 0; j < cols; j++) {
                    mapHtml += `
                        <td id="${i}${j}">
                            <button class="btn" onclick="handleCellClick(${i}, ${j}, \`${JSON.stringify(data).replace(/"/g, '&quot;')}\`)">
                                ${map[i][j]}
                            </button>
                        </td>
                    `;
                }
                mapHtml += "</tr>";
            }
            mapHtml += "</table>";

            // Update the map section with rows, cols, and the map table
            document.getElementById("map-section").innerHTML = mapInfo + mapHtml;
        })
        .catch(error => console.error('Error fetching map:', error));
}

// Function to handle button clicks
function handleCellClick(row, col, dataStr) {
    document.getElementById(`${row}${col}`).style.backgroundColor = 'lightblue';
    setTimeout(() => {
        document.getElementById(`${row}${col}`).style.backgroundColor = '';
    }, 2000);

    const data = JSON.parse(dataStr);   
    const map = data.data;
    const mines_db = data.mines_db;

    if (map[row][col] === 1) {
        const serialNum = mines_db[`${row},${col}`] || "Unknown";

        document.getElementById("mineinfo-section").innerHTML = `
            <b><p>(x, y): (${row}, ${col})</p>
            <p>Serial Num: ${serialNum}</p></b>
        `;
    } else {
        document.getElementById("mineinfo-section").innerHTML = `
            <b><p>(x, y): (${row}, ${col})</p></b>
        `;
    }
}

function updateMap() {
    const rows = document.getElementById("mapRows").value;
    const cols = document.getElementById("mapCols").value;

    if (!rows || !cols) {
        alert("Please enter valid row and column numbers.");
        return;
    }

    // Create the map object to send (data is not included here)
    const mapObject = {rows: parseInt(rows), cols: parseInt(cols)};

    // Make the PUT request (without sending data if not needed)
    fetch(`${baseUrl}/map`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(mapObject)
    })
    .then(response => response.json())
    .then(data => {
        const map = data.data;
        const rows = data.rows;
        const cols = data.cols;
        const mapInfo = `<div><p>Rows: ${rows}<br/>Columns: ${cols}</p></div>`;
        // Generate HTML for the map table
        let mapHtml = "<table class='table table-bordered text-center d-flex justify-content-center'>";
        for (let i = 0; i < rows; i++) {
            mapHtml += "<tr>";
            for (let j = 0; j < cols; j++) {
                mapHtml += `<td>${map[i][j]}</td>`;
            }
            mapHtml += "</tr>";
        }
        mapHtml += "</table>";

        // Update the map section in the DOM
        document.getElementById("map-section").innerHTML = mapInfo + mapHtml;
        document.getElementById("mapRows").value = 0;
        document.getElementById("mapCols").value = 0;
    })
    .catch(error => console.error('Error updating map:', error));
}

function getMines() {
    fetch(`${baseUrl}/mines`, { method: "GET" })
        .then(response => response.json())
        .then(mines => {
            let minesList = "<div>";
            mines.forEach(mine => {
                if (mine.x !== null && mine.y !== null) {
                    minesList += `<p><b>ID: ${mine.mine_id}</b> - ${mine.serial_number} <b>(${mine.x}, ${mine.y})</b></p>`;
                } else {
                    minesList += `<p><b>ID: ${mine.mine_id}</b> - ${mine.serial_number}</p>`;
                }
            });
            minesList += "</div>";
            document.getElementById("mines-section1").innerHTML = minesList;
        })
        .catch(error => {
            document.getElementById("mines-section1").innerHTML = "<p>Error fetching mines</p>";
        });
}


function getMineById() {
    const mineId = document.getElementById("mineID").value;
    if (!mineId) {
        alert("Please enter valid mine ID.");
        return;
    }
    fetch(`${baseUrl}/mines/${mineId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            let mineDetails = `<p>Mine ID: ${data.mine_id}<br/>Serial Number: <b>${data.serial_number}</b></p>`;
            if (data.x !== null && data.y !== null) {
                mineDetails += `<p>(${data.x}, ${data.y})</p>`;
            } else {
                mineDetails += `<p>Mine is not placed on map.</p>`;
            }
            document.getElementById("mines-section2").innerHTML = mineDetails;
            document.getElementById("getMineForm").reset();
        })
        .catch(error => {
            document.getElementById("mines-section2").innerHTML = "<p>Error fetching the mine</p>";
        });
}


function addMine() {
    const serialNum = document.getElementById("serialNum").value;
    const row = parseInt(document.getElementById("xAdd").value);
    const col = parseInt(document.getElementById("yAdd").value);
    if (!serialNum || serialNum.length !== 10) {
        alert("Please enter a valid 10-digit serial number.");
        return;
    }
    fetch(`${baseUrl}/map/size`)
        .then(response => response.json())
        .then(mapData => {
            const { rows, cols } = mapData; 
            console.log(rows, cols, row, col);

            if (row < 0 || row >= rows || col < 0 || col >= cols) {
                alert(`Coordinates must be between 0 and ${rows - 1} for rows and 0 and ${cols - 1} for columns.`);
                return;
            }

            fetch(`${baseUrl}/mines`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    serial_number: serialNum, x: row, y: col
                })
            })
            .then(response => response.json())
            .then(data => {
                const newMineId = data.mine_id;
                const message = data.message;
                getMines();
                document.getElementById("mines-section3").innerHTML = `<p>Mine ID: ${newMineId}<br/><b>${message} at (${data.x}, ${data.y}). Please check the map.</b></p>`;
                document.getElementById("addMineForm").reset();
                getMap();
            })
            .catch(error => alert('Error adding mine: ' + error));
        })
        .catch(error => alert('Error fetching map data: ' + error));
}


// Delete a mine by ID
function deleteMine() {
    const mineId = document.getElementById("mineIdToDelete").value;  // Get mine ID from input field

    if (!mineId) {
        alert("Please enter a valid mine ID.");
        return;
    }

    // Make a DELETE request to remove the mine by ID
    fetch(`${baseUrl}/mines/${mineId}`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        }
    })
    .then(response => response.json())
    .then(data => {
        const message = data.message;  // Response message
        const deletedMine = data.deleted_mine;  // Deleted mine object
        console.log(data);
        
        // Display a success message with the deleted mine details
        document.getElementById("mines-section4").innerHTML = `
            <p><b>Mine ID:</b> ${deletedMine.mine_id}</p>
            <p><b>Serial Number:</b> ${deletedMine.serial_number}</p><br/>
            <p>Please check the map.</p>
            <b>${message}</b>
        `;

        getMines();  // Refresh the list of mines
        getMap();
        document.getElementById("deleteMineForm").reset();
    })
    .catch(error => alert('Error deleting mine: ' + error));
}

function getRovers() {
    fetch(`${baseUrl}/rovers`)
        .then(response => response.json())
        .then(data => {
            // Assuming data is an array of rover objects returned from the backend
            const rovers = data;
            const roversSection = document.getElementById("rovers-section1");  // The div where rovers will be displayed
            roversSection.style.width = "85%";
            // Clear the current contents in the collapsible section
            const roversCollapse = document.getElementById("roversCollapse");
            roversCollapse.innerHTML = ""; // Clear existing content

            // Loop through each rover and create HTML to display them
            const roversContainer = document.createElement("div");

            rovers.forEach(rover => {
                const roverDiv = document.createElement("div");
                roverDiv.classList.add("rover-item");
                roverDiv.innerHTML = `
                    <p><strong>Rover ID:</strong> ${rover.rover_id}, <strong>Status:</strong> ${rover.status}</p>
                    <p style="overflow: scroll;"><strong>Commands:</strong> ${rover.commands}</p>
                    <hr>
                `;
                roversContainer.appendChild(roverDiv);
            });

            // Append the rovers to the collapsible section
            roversCollapse.appendChild(roversContainer);

            // Ensure the roversCollapse section is now visible after content is added
            new bootstrap.Collapse(roversCollapse, {
                toggle: true
            });
        })
        .catch(error => {
            console.error('Error fetching rovers:', error);
            alert('Error fetching rovers');
        });
}


// Fetch specific rover by ID based on form input
function getRoverById(event) {
    event.preventDefault(); // Prevent the default tab switch behavior
    
    const roverId = document.getElementById("roverID").value;  // Get value from the input field
    if (roverId) {
        fetch(`${baseUrl}/rovers/${roverId}`)
            .then(response => response.json())
            .then(data => {
                // Update the UI with the rover data
                document.getElementById("rovers-section2").innerHTML = `
                    <p><strong>Rover ID:</strong> ${data.rover_id}, <strong>Status:</strong> ${data.status}</p>
                    <p style="overflow: scroll;"><strong>Commands:</strong> ${data.commands}</p>
                `;
                
                // Switch to the "View Specific Rover" tab programmatically
                const myTabs = new bootstrap.Tab(document.getElementById('section2-tab'));
                myTabs.show();
            })
            .catch(error => {
                document.getElementById("rovers-section2").innerHTML = "<p>Error fetching the rover</p>";
            });
    } else {
        document.getElementById("rovers-section2").innerHTML = "<p>Please enter a valid Rover ID</p>";
    }
}


function createRover() {
    const roverCommands = document.getElementById("roverCommands").value;
    if (!roverCommands) {
        alert("Please enter rover commands.");
        return;
    }

    fetch(`${baseUrl}/rovers`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ commands: roverCommands }),  // Corrected to match the API's expected body
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("rovers-section3").innerHTML = `
            <p>Rover Created Successfully!</p>
            <p><b>ID:</b> ${data.rover_id}</p>
            <p><b>Commands:</b> ${data.commands}</p>
            <p><b>Status:</b> ${data.status}</p>
            <p><b>${data.message}</b></p>
        `;
        document.getElementById('createRoverForm').reset();
    })
    .catch(error => {
        document.getElementById("rovers-section3").innerHTML = "<p>Error creating the rover.</p>";
    });
}

function deleteRover() {
    const roverId = document.getElementById("roverIdToDelete").value;  // Get the rover ID from the input field
    if (!roverId) {
        alert("Please enter the Rover ID to delete.");
        return;
    }

    // Send DELETE request to the backend API
    fetch(`${baseUrl}/rovers/${roverId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())  // Parse the JSON response
    .then(data => {
        // Display the response message in the rovers-section4 div
        document.getElementById("rovers-section4").innerHTML = `
            <p>${data.message}</p>
            <p>Please view all rovers again to confirm.</p>
        `;

        getRovers();
        document.getElementById('deleteRoverForm').reset();
    })
    .catch(error => {
        // Handle errors by displaying an error message
        document.getElementById("rovers-section4").innerHTML = "<p>Error deleting the rover.</p>";
    });
}


function dispatchRover() {
    const roverId = document.getElementById("roverIdToDispatch").value;
    if (!roverId) {
        alert("Please enter the Rover ID to dispatch.");
        return;
    }

    // Disable the button to avoid multiple clicks
    document.getElementById("dispatchRoverForm").querySelector("button").disabled = true;
    document.getElementById("dispatchRoverForm").querySelector("button").textContent = 'Loading...';

    // Dispatch the rover
    fetch(`${baseUrl}/rovers/${roverId}/dispatch`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            const { xPos, yPos, status, commands } = data;
            document.getElementById("rovers-section5").innerHTML = `
                <p><b>Rover ${roverId} dispatched successfully!</b></p>
                <p><b>Status:</b> ${status}</p>
                <p style="overflow: scroll;"><b>Commands:</b> ${commands}</p>
                <p><b>Position:</b> (${xPos}, ${yPos})</p>
            `;
            
            // Polling for rover status completion
            pollRoverStatus(roverId);
        })
        .catch(error => {
            // Enable the button again on failure
            document.getElementById("dispatchRoverForm").querySelector("button").disabled = false;
            alert('Error dispatching rover: ' + error.message);
        });
}

function pollRoverStatus(roverId) {
    const intervalId = setInterval(() => {
        // Fetch the rover's status
        fetch(`${baseUrl}/rovers/${roverId}`)
            .then(response => response.json())
            .then(statusData => {
                const { status } = statusData.status;

                if (status !== "Not_Started") {
                    clearInterval(intervalId);
                    // Once done, fetch the map
                    generateMapWithRoverPath(roverId);
                    toggleLogs();
                    document.getElementById("dispatchRoverForm").querySelector("button").disabled = false;
                    document.getElementById("dispatchRoverForm").querySelector("button").textContent = 'Dispatch Rover';
                }
            })
            .catch(error => {
                console.error("Error checking rover status:", error);
                clearInterval(intervalId);  // Stop polling in case of error
                alert("Error checking rover status.");
            });
    }, 2000); // Check every 2 seconds (adjust as needed)
}

function generateMapWithRoverPath(roverId) {
    // Fetch the map size first
    fetch(`${baseUrl}/map/size`)
        .then(response => response.json())
        .then(([rows, cols]) => {
            // Fetch the map grid for the rover
            fetch(`${baseUrl}/map/grid/${roverId}`)
                .then(response => response.json())
                .then(mapArray => {
                    let mapHtml = "<table class='table table-bordered text-center d-flex justify-content-center'>";

                    for (let i = 0; i < rows; i++) {
                        mapHtml += "<tr>";
                        for (let j = 0; j < cols; j++) {
                            mapHtml += `
                                <td id="${i}${j}">
                                    ${mapArray[i][j]}
                                </td>
                            `;
                        }
                        mapHtml += "</tr>";
                    }
                    mapHtml += "</table>";

                    // Display the map in the appropriate section
                    document.getElementById("map-result").innerHTML = mapHtml;
                })
                .catch(error => {
                    console.error('Error fetching path data:', error);
                    document.getElementById("map-result").innerHTML = 'Error fetching map data.';
                });
        })
        .catch(error => {
            console.error('Error fetching map size:', error);
            document.getElementById("map-result").innerHTML = 'Error fetching map size.';
        });
}


// Handling of dispatched rover logs

function toggleLogs() {
    const roverId = document.getElementById('roverIdToDispatch').value;
    logsVisible = !logsVisible;
    const logsSection = document.getElementById('logs-section');
    const toggleButton = document.getElementById('toggleLogsButton');

    if (logsVisible) {
        logsSection.style.display = 'block';
        toggleButton.textContent = 'Hide Logs';
        fetchLogs(roverId);
    } else {
        logsSection.style.display = 'none';
        toggleButton.textContent = 'Show Logs';
    }
}

function fetchLogs(roverId) {
    if (!roverId) {
        alert("Please enter a Rover ID to view logs.");
        return;
    }

    fetch(`${baseUrl}/logs/${roverId}`)
        .then(response => response.text())
        .then(data => {
            const logsContent = document.getElementById('logsContent');
            let formattedLogs = data.replace(/\\n/g, '<br/>').replace(/"/g, '');
            logsContent.innerHTML = formattedLogs;
        })
        .catch(error => {
            document.getElementById('logsContent').textContent = 'Error fetching logs: ' + error.message;
        });
}


function resetRovers() {
    fetch(`${baseUrl}/rovers/reset`)
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => {
            console.error('Error resetting rovers:', error);
        });
}
