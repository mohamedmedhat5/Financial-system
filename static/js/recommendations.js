const btn = document.getElementById("recommend-btn");

const result = document.getElementById(
    "recommendation-result"
);

btn.addEventListener("click", async () => {

    btn.disabled = true;

    result.innerHTML = "Generating...";

    const payload = {

        amount: Number(
            document.getElementById("invest-amount").value
        ),

        duration_years: Number(
            document.getElementById("invest-duration").value
        ),

        risk_tolerance:
            document.getElementById("invest-risk").value,

        goal:
            document.getElementById("invest-goal").value

    };

    try {

        const response = await fetch(

            "/api/recommendation",

            {

                method: "POST",

                headers: {

                    "Content-Type": "application/json"

                },

                body: JSON.stringify(payload)

            }

        );

        const data = await response.json();

        if (!response.ok) {

            result.innerHTML =

                `<p>${data.error}</p>`;

            return;

        }

        let html = `

        <h2>Recommended Portfolio</h2>

        <br>

        `;

                data.allocation.forEach(item => {

            html += `

            <div class="recommend-item">

                <h3>${item.asset}</h3>

                <p>

                    <strong>

                        ${item.percentage}%

                    </strong>

                </p>

                <p>

                    ${Number(item.amount)
                        .toLocaleString()}

                </p>

                <small>

                    ${item.explanation}

                </small>

                <hr>

            </div>

            `;

        });

        html += `

        <div class="summary">

            <h3>

                Why?

            </h3>

            <p>

                ${data.summary}

            </p>

        </div>

        `;

        result.innerHTML = html;

    }

    catch (err) {

        result.innerHTML =

            "Server Error";

    }

    btn.disabled = false;

});