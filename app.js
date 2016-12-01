var solve = window['twenty_four'].solve_main;

function parse(input) {
    return input.replace(/[^\d,]/g, '').split(',').map(function(s) {
        return parseInt(s);
    });
}

function submit() {
    var requiredNumber = 4;
    var target = 24;
    var $output = $("#output");
    var input = $('#input-numbers').val();
    var numbers = parse(input);
    if (numbers.length < requiredNumber) {
        $output.html('<h2><span class="tag tag-info">too few numbers</span></h2>');
        return;
    }
    if (numbers.length > requiredNumber) {
        $output.html('<h2><span class="tag tag-warning">your phone could burn</span></h2>');
        return;
    }
    var solutions = solve(numbers);
    if (solutions.length == 0) {
        $output.html('<h2><span class="tag tag-danger">no solution</span></h2>');
        return;
    }
    var outArray = solutions.map(function (s) {
        var t = s.replace(/\*/g, '\u00D7').replace(/\//, '\u00F7');
        return t + ' = ' + target;
    });
    $output.html('<br />'.join(outArray) + '<h4><span class="tag tag-success">and you thought of nothing?</span></h4>');
}

$('#input-numbers').on('input', function() {
    submit();
});
