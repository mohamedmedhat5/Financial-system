// static/js/predictions.js

$$(".predict-button").forEach(button => {

    on(button, "click", async () => {

        const model = button.dataset.model;

        const card = button.closest(".prediction-card");

        const result = $(".prediction-result", card);

        button.disabled = true;

        result.textContent = "Predicting...";

        let endpoint = "";
        let payload = {};

        switch(model){

            case "salary":

                endpoint="/api/predict-salary";

                payload={

                    age:Number($("#salary-age").value),

                    gender:$("#salary-gender").value,

                    education_level:$("#salary-education").value,

                    job_title:$("#salary-job").value,

                    years_of_experience:Number($("#salary-exp").value)

                };

            break;

            case "expense":

                endpoint="/api/predict-expense";

                payload={

                    year:Number($("#expense-year").value),

                    month:Number($("#expense-month").value),

                    income:Number($("#expense-income").value),

                    income_bracket:$("#expense-income-bracket").value,

                    festival:$("#expense-festival").value,

                    festival_count:Number($("#expense-festival-count").value)

                };

            break;

            case "cost":

    endpoint="/api/predict-cost-living";

payload = {

    cost_of_living_index:
        Number($("#cost-index").value),

    rent_index:
        Number($("#rent-index").value),

    cost_of_living_plus_rent_index:
        Number($("#living-rent").value),

    groceries_index:
        Number($("#groceries-index").value),

    restaurant_price_index:
        Number($("#restaurant-index").value),

    local_purchasing_power_index:
        Number($("#purchasing-power").value),

    income_to_cost_ratio:
        Number($("#income-ratio").value)

};

break;

            case "inflation":

                endpoint="/api/predict-inflation";

                payload = {

    year: Number($("#inflation-year").value),

    lag_1: Number($("#lag-1").value),

    lag_2: Number($("#lag-2").value),

    lag_3: Number($("#lag-3").value),

    rolling_mean_3: Number($("#rolling-mean").value),

    rolling_std_3: Number($("#rolling-std").value)

};

            break;

            case "recommendation":

                endpoint="/api/recommendation";

                payload={

                    amount:Number($("#invest-amount").value),

                    duration_years:Number($("#invest-duration").value),

                    risk_tolerance:$("#invest-risk").value,

                    goal:$("#invest-goal").value

                };

            break;

        }

        try{

            const response=await fetch(endpoint,{

                method:"POST",

                headers:{
                    "Content-Type":"application/json"
                },

                body:JSON.stringify(payload)

            });

            const data=await response.json();

            if(response.ok){

if(data.prediction !== undefined){

    switch(model){

        case "salary":

            result.innerHTML = `

                <small>Estimated Annual Salary</small>

                <h2>$${Number(data.prediction).toLocaleString()}</h2>

            `;

        break;

        case "expense":

            result.innerHTML = `

                <small>Estimated Monthly Expense</small>

                <h2>$${Number(data.prediction).toLocaleString()}</h2>

            `;

        break;

        case "cost":

            result.innerHTML = `

                <small>Predicted Cost Of Living Index</small>

                <h2>${Number(data.prediction).toFixed(0)}</h2>

            `;

        break;

        case "inflation":

            result.innerHTML = `

                <small>Predicted Inflation Rate</small>

                <h2>${Number(data.prediction).toFixed(2)}%</h2>

            `;

        break;

        default:

            result.innerHTML = `

                <small>Prediction Result</small>

                <h2>${data.prediction}</h2>

            `;

    }

}

    else if(data.allocation){

        let html=`

            <h3>Recommended Portfolio</h3>

            <br>

        `;

        data.allocation.forEach(item=>{

            html+=`

            <div class="allocation-item">

                <strong>${item.asset}</strong>

                <br>

                ${item.percentage}% |

                ${item.amount.toLocaleString()}

                <br>

                <small>${item.explanation}</small>

                <br><br>

            </div>

            `;

        });

        html+=`

        <hr>

        <p>${data.summary}</p>

        `;

        result.innerHTML=html;

    }

    card.classList.add("is-complete");

}

else{

    result.textContent=data.error;

}

        }

        catch(err){

            result.textContent="Server Error";

        }

        button.disabled=false;

    });

});

// ===============================
// Inflation Auto Calculation
// ===============================

function updateInflationStats() {

    const lag1 = Number($("#lag-1")?.value) || 0;
    const lag2 = Number($("#lag-2")?.value) || 0;
    const lag3 = Number($("#lag-3")?.value) || 0;

    const values = [lag1, lag2, lag3];

    const mean =
        values.reduce((sum, value) => sum + value, 0) /
        values.length;

    const variance =
        values.reduce(
            (sum, value) =>
                sum + Math.pow(value - mean, 2),
            0
        ) / values.length;

    const std = Math.sqrt(variance);

    if ($("#rolling-mean"))
        $("#rolling-mean").value = mean.toFixed(2);

    if ($("#rolling-std"))
        $("#rolling-std").value = std.toFixed(2);
}

if ($("#lag-1")) {

    ["lag-1", "lag-2", "lag-3"].forEach(id => {

        $("#" + id).addEventListener(
            "input",
            updateInflationStats
        );

    });

    updateInflationStats();
}