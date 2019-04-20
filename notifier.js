console.log('Импорт библиотек...');
args = require('args');
var request = require("request");
var colour = require('colour');
var nhp = require('node-html-parser');


// import complete

function msleep(n) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, n);
}
function sleep(n) {
  msleep(n*1000);
}
function makeid(length) {
  var text = "";
  var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";

  for (var i = 0; i < length; i++)
    text += possible.charAt(Math.floor(Math.random() * possible.length));

  return text;
}

colour.setTheme({
  silly: 'rainbow',
  input: 'grey',
  verbose: 'cyan',
  prompt: 'grey',
  info: 'green',
  data: 'grey',
  help: 'cyan',
  warn: ['yellow', 'underline'],
  debug: 'blue',
  error: 'red bold'
});
console.log('Импорт библиотек завершен.'.green);

args
  .option('m', 'Manga ID')
  .option('u', 'Callback URL')
  .option('t', 'Interval in seconds', 15)


const flags = args.parse(process.argv)

if(flags.m == undefined)
{
	console.log("Ошибка: Не указан ID манги!".red);
	console.log("Пример: ".help+"node notifier.js -m naruto -u http://example.com/example.php".warn);
	process.exit(1);
}
if(flags.u == undefined)
{
	console.log("Ошибка: Не указан URL отправки!".red);
	console.log("Пример: ".help+"node notifier.js -m naruto -u http://example.com/example.php".warn);
	process.exit(1);
}


request(
    { uri: "https://mangalib.me/"+flags.m },
    function(error, response, body) {
        var isitbad = nhp.parse(response.body);
        if(isitbad.querySelector(".error-page") == null){

console.clear();
var manganame = isitbad.querySelector('.manga__title').innerHTML;
console.log('Загрузка завершена. Отслеживаем мангу '+manganame+' ('+flags.m+') каждые '+flags.t+" сек.");
var chapter = isitbad.querySelector('.chapter-item__icon').attributes['data-id'];
console.log('ID текущей главы: '+chapter+'.');
console.log('Ожидаем изменения...'.help);
console.log('Callback URL: '+flags.u);
var secret = makeid(7);
console.log('Секретный ключ: '+secret.help);
console.log('Работа начата. CTRL+C для выхода.'.green);

setInterval(function(){
	request({ uri: "https://mangalib.me/"+flags.m },
	function(error, response,body) {
		var is2 = nhp.parse(response.body);
		var chaptern = isitbad.querySelector('.chapter-item__icon').attributes['data-id'];
		console.log('Обновлено. ID последней главы: '+chaptern);
		if(chapter == chaptern){
			console.log('Новая глава манги не вышла, продолжаю ждать...'.red);
		} else {
			console.log('Вышла новая глава манги! Отправляю запрос...'.green);
			request({uri: flags.u+"/?secret="+secret+"&id="+chaptern},function(){ console.log('Запрос отправлен. Ожидаем новую главу...'); });
			chapter = chaptern;
		}
	});
}, flags.t*1000);

        }
        else {
        	console.log('Ошибка: '.red+'Манги с таким ID на mangalib нет!'.help);
        }
        
    }
);



