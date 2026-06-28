import React from 'react';
import { FlexWidget, TextWidget, ImageWidget, OverlapWidget } from 'react-native-android-widget';

export function MenuWidget({ menuData, nextMealType, targetDateStr }) {
  if (!menuData || !targetDateStr) {
    return (
      <FlexWidget
        style={{
          height: 'match_parent',
          width: 'match_parent',
          backgroundColor: '#1a1a1a',
          justifyContent: 'center',
          alignItems: 'center',
          borderRadius: 24,
        }}
      >
        <TextWidget text="メニュー情報を取得中..." style={{ color: '#E0E0E0', fontSize: 18 }} />
      </FlexWidget>
    );
  }

  const mealInfo = menuData[targetDateStr]?.[nextMealType];
  if (!mealInfo) {
    return (
      <FlexWidget style={{ height: 'match_parent', width: 'match_parent', backgroundColor: '#1a1a1a', justifyContent: 'center', alignItems: 'center', borderRadius: 24 }}>
        <TextWidget text="データがありません" style={{ color: '#E0E0E0', fontSize: 18 }} />
      </FlexWidget>
    );
  }

  const emoji = nextMealType === 'breakfast' ? '🌅' : nextMealType === 'lunch' ? '🍱' : '🥩';
  const mealNameJp = nextMealType === 'breakfast' ? '朝食' : nextMealType === 'lunch' ? '昼食' : '夕食';
  const [year, month, day] = targetDateStr.split('-');

  return (
    <OverlapWidget
      style={{
        height: 'match_parent',
        width: 'match_parent',
        borderRadius: 24,
      }}
    >
      <FlexWidget style={{ width: 'match_parent', height: 'match_parent', backgroundColor: '#1a1a1a' }} />
      
      {mealInfo.image_url ? (
        <ImageWidget
          image={mealInfo.image_url}
          imageWidth={400}
          imageHeight={250}
          style={{
            width: 'match_parent',
            height: 'match_parent',
          }}
        />
      ) : null}

      <FlexWidget
        style={{
          width: 'match_parent',
          height: 'match_parent',
          backgroundColor: 'rgba(26, 26, 26, 0.9)',
        }}
      />

      <FlexWidget
        style={{
          height: 'match_parent',
          width: 'match_parent',
          justifyContent: 'space-between',
          padding: 25,
        }}
      >
        <FlexWidget style={{ flexDirection: 'column' }}>
          <TextWidget
            text={`${emoji} ${parseInt(month)}月${parseInt(day)}日の${mealNameJp}`}
            style={{ color: '#FFB74D', fontSize: 16, fontWeight: 'bold', marginBottom: 8 }}
          />
          <TextWidget
            text={mealInfo.main_dish}
            style={{ color: '#FFFFFF', fontSize: 26, fontWeight: 'bold' }}
          />
        </FlexWidget>
        
        <FlexWidget style={{ flexDirection: 'column' }}>
          {mealInfo.side_dishes ? (
            <TextWidget
              text={`副菜: ${mealInfo.side_dishes}`}
              style={{ color: '#E0E0E0', fontSize: 14, marginBottom: 8 }}
            />
          ) : null}
          <TextWidget
            text={`⏰ 時間: ${mealInfo.time}`}
            style={{ color: '#FFCC80', fontSize: 18, fontWeight: 'bold' }}
          />
        </FlexWidget>
      </FlexWidget>
    </OverlapWidget>
  );
}
