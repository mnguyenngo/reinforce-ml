let get_submission = function() {
    let q = $("textarea#user-submission").val()
    return q
};

let send_submission_json = function(submission) {
    $.ajax({
        url: '/submit',
        contentType: "application/json; charset=utf-8",
        type: 'POST',
        data: JSON.stringify(submission),
        success: function (data) {
            display_results(data);
        }
    });
    console.log(submission)
};

let display_results = function(results) {
    let user_submission = $("div#show-user-submission")
    user_submission.html(results)
};

$(document).ready(function() {
    $("button#submit").click(function() {
        let submission = get_submission();
        send_submission_json(submission);
    })
})
