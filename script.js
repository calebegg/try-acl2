window.onresize = resize;
sid = Math.random();
current_section = 0;
function resize() {
  pre_width = pre.width();
  if (pre_width > 800) {
    setTimeout(resize, 100);
    return;
  }
  outer_console.width(pre_width + 10);
  tutorial.width(body.width() - pre_width + 10);
  info.css('right', pre_width - info.width() - 35 + 'px');
  jq_console.height(outer_console.height() - $('h1').height() - 10);
}
opacity = 0;
function showPrevSection() {
  if (current_section === 0) {
    return;
  } else {
    sections.eq(current_section).hide();
    current_section--;
    sections.eq(current_section).show();
  }
}
function showNextSection() {
  if (current_section >= sections.length - 1) {
    return;
  } else {
    sections.eq(current_section).hide();
    current_section++;
    sections.eq(current_section).show();
  }
}
function main() {
  // Globals
  jq_console = $('#jq-console');
  outer_console = $('#console');
  console_inner = $('.jquery-console-inner');
  pre = $('#ref');
  body = $('body');
  tutorial = $('article');
  info = $('aside');
  sections = $('section');
  throbber = $('#throbber');
  resize();
  // Set up tutorial
  sections.hide();
  sections.eq(0).show();
  $('#prev').click(showPrevSection);
  $('#next').click(showNextSection);
  // Shadow effect on scrolled console
  function consoleShadowScrollHandler() {
    if (this.scrollTop > 0) {
      old_opacity = opacity;
      opacity = Math.min(this.scrollTop, 20) / 20 / 6 + .05;
      if (opacity != old_opacity) {
        outer_console.css('box-shadow', "2px 2px 8px rgba(0, 0, 0, .2), " +
          " 0 15px 10px -10px rgba(0,0,0," + opacity + ") inset");
      }
    } else {
      outer_console.css('box-shadow', '');
    }
  }
  outer_console.scroll(consoleShadowScrollHandler);
  controller = jq_console.console(
    {
      autofocus: true,
      promptLabel: '> ',
      commandValidate: function(line) {
        if (line === "") {
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
            $($(this).children()[1]).toggle(1);
          });
          collapse_box.append(message = $('<div>'));
          collapse_box.append($('<div>')
                                .text(data)
                                .hide()
                                .addClass('jquery-console-message'));
          if (data.match('FAILED')) {
            message.text('Failed. (click for details)').addClass('failure');
            report(collapse_box);
          } else if (data.match('Proof succeeded.') || data.match('trivial')) {
            message.text('Succeeded. (click for details)').addClass('success');
            report(collapse_box);
          } else{
            report(data);
          }
          jq_console.css('opacity', '1');
          throbber.hide();
          outer_console_elem = outer_console[0];
          outer_console_elem.scrollTop = outer_console_elem.scrollHeight;
        });
      }
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
