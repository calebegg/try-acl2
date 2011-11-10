window.onresize = resize;
sid = Math.random()
prev = $('<input id="prev" type="button" value="&lt;" />');
next = $('<input id="next" type="button" value="&gt;" />');
function resize() {
  pre_width = pre.width();
  outer_console.width(pre_width + 10);
  tutorial.width(body.width() - pre_width + 10);
  info.css('right', pre_width - info.width() - 35 + 'px');
  jq_console.height(outer_console.height() - $('h1').height() - 10);
}
function main() {
  jq_console = $('#jq-console');
  outer_console = $('#console');
  console_inner = $('.jquery-console-inner');
  pre = $('pre');
  body = $('body');
  tutorial = $('article');
  info = $('aside');
  resize();
  tutorial.append(prev);
  tutorial.append(next);
  prev.click(function(){alert('prev');});
  next.click(function(){alert('next');});
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
          data = data.trim();
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
          outer_console_elem = outer_console[0];
          outer_console_elem.scrollTop = outer_console_elem.scrollHeight;
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
}
$(main);
function parens_match(line) {
  opens = line.match(/\(/g);
  open_cnt = (opens ? opens.length : 0);
  closes = line.match(/\)/g);
  close_cnt = (closes ? closes.length : 0);
  return open_cnt - close_cnt;
}
