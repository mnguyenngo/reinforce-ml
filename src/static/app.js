let get_submission = function() {
    let u = $("textarea#user-submission").val();
    let word = $("span#word").text();
    return {'user_subm': u, 'word': word}
};

let send_submission_json = function(submission) {
    console.log(submission)

    $.ajax({
        url: '/submit',
        contentType: "application/json; charset=utf-8",
        type: 'POST',
        data: JSON.stringify(submission),
        success: function (data) {
            display_results(data);
        }
    });
};

let display_results = function(results) {
    let user_submission = $("div#submission")
    user_submission.html(results.submission)
    let score = $("div#score")
    user_submission.html(results.score)
};

$(document).ready(function() {
    $("button#submit").click(function() {
        let submission = get_submission();
        send_submission_json(submission);
    })
})
