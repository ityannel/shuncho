import React from 'react';
import { WidgetTaskHandlerProps } from 'react-native-android-widget';
import { MenuWidget } from './Widget';

export async function widgetTaskHandler(props: WidgetTaskHandlerProps) {
  let menuData = null;
  let targetDateStr = null;
  let nextMealType = null;

  try {
    const res = await fetch('https://ityannel.github.io/shuncho/menu.json?' + Date.now());
    menuData = await res.json();
    
    const now = new Date();
    // Use SV format to get local YYYY-MM-DD
    const todayStr = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().split('T')[0];
    const tomorrow = new Date(now.getTime() + 86400000);
    const tomorrowStr = new Date(tomorrow.getTime() - tomorrow.getTimezoneOffset() * 60000).toISOString().split('T')[0];
    
    const datesToCheck = [todayStr, tomorrowStr];

    const meals = [
        { key: 'breakfast', name: '朝食', emoji: '🌅' },
        { key: 'lunch', name: '昼食', emoji: '🍱' },
        { key: 'dinner', name: '夕食', emoji: '🥩' }
    ];

    for (const dStr of datesToCheck) {
        if (!menuData[dStr]) continue;
        const dayMenu = menuData[dStr];
        
        for (const meal of meals) {
            const mealData = dayMenu[meal.key];
            if (!mealData || !mealData.time) continue;
            
            const [hour, minute] = mealData.time.split(':');
            const tTime = new Date(`${dStr}T${hour}:${minute}:00`);

            if (tTime > now) {
                targetDateStr = dStr;
                nextMealType = meal.key;
                break;
            }
        }
        if (targetDateStr) break;
    }
  } catch(e) {
    console.error(e);
  }

  switch (props.widgetAction) {
    case 'WIDGET_ADDED':
    case 'WIDGET_UPDATE':
    case 'WIDGET_RESIZED':
      props.renderWidget(
        <MenuWidget 
            menuData={menuData} 
            targetDateStr={targetDateStr} 
            nextMealType={nextMealType} 
        />
      );
      break;
    default:
      break;
  }
}
