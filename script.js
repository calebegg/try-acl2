sid = Math.random()
  function parens_match(line) {
    opens = line.match(/\(/g);
    open_cnt = (opens ? opens.length : 0);
    closes = line.match(/\)/g);
    close_cnt = (closes ? closes.length : 0);
    return open_cnt - close_cnt;
  }
function insert(code) {

}
var consoleCancelFlag = false;
$(document).ready(function(){
  // Set up the console.
  jq_console = $('#console');
  throbber = $('#throbber');
  controller = jq_console.console(
    {
      autofocus: true,
      promptLabel: '> ',
      commandValidate: function(line) {
        if (line == "") {
          return false;
        } else {
          return true;
        }
      },
      commandHandle: function(line, report) {
        jq_console.css('opacity', '.8');
        throbber.show();
        paren_count = parens_match(line);
        if (paren_count > 0) {
          controller.continuedPrompt = true;
          return;
        } else if (paren_count < 0) {
          report([{msg:"Unmatched ')'", className:"error"}]);
          return;
        }
        controller.continuedPrompt = false;
        $.get('', {code: line, sid: sid}, function(data) {
          collapse_box = $('<div class="collapse"></div>');
          collapse_box.click(function() {
            $($(this).children()[0]).toggle(1);
          });
          if (data.match('Proof succeeded.')) {
            collapse_box.text('Succeeded. (click for details)');
            collapse_box.addClass('success');
            collapse_box.append($('<div>').text(data).hide().addClass('jquery-console-message'));
            report(collapse_box);
          } else if (data.match('FAILED')) {
            report(data);
          } else{
            report(data);
          }
          jq_console.css('opacity', '1');
          throbber.hide();
          inner = $('.jquery-console-inner')[0]
            inner.scrollTop = inner.scrollHeight;
        });
      },
  });
  // Add links to <code> elements.
  $('code').each(function() {
    $(this).click(function() {
      controller.promptText($(this).text());
      controller.inner.click();
    });
  });
});
