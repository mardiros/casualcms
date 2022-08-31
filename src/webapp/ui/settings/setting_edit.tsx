import React from "react";
import { Box, Heading } from "@chakra-ui/react";
import { withTheme } from "@rjsf/core";
import { Theme as ChakraUITheme } from "@rjsf/chakra-ui";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useAuth } from "../login/hooks";
import { ApiError } from "../../casualcms/domain/ports";
import { AppContext } from "../../config";
import { Setting, SettingType } from "../../casualcms/domain/model";
import { Loader } from "../layout/loader";
import { ApiErrorUI } from "../layout/error_api";
import { SettingBreadcrumb } from "../layout/breadcrumb";
// import { SettingBreadcrumb } from "../layout/breadcrumb";

const Form = withTheme(ChakraUITheme);

export const SettingEdit: React.FunctionComponent<{}> = () => {
  let auth = useAuth();
  const config = React.useContext(AppContext);
  const token = auth.authenticatedUser?.token || "";
  const [setting, setSetting] = React.useState<Setting | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const params = useParams();
  const settingKey = params.settingKey || "";
  const hostname = params.hostname || "";

  const [settingType, setSettingType] = React.useState<SettingType | null>(
    null
  );
  const [error, setError] = React.useState<ApiError>(null);
  let navigate = useNavigate();

  React.useEffect(() => {
    async function loadSettingType() {
      const rtyp = await config.api.settingType.showSettingType(
        token,
        settingKey
      );
      rtyp
        .map((typ: SettingType) => setSettingType(typ))
        .mapErr((err: ApiError) => setError(err));
    }
    loadSettingType();
    return () => {
      setIsLoading(true);
      setError(null);
      setSettingType(null);
    };
  }, [settingKey]);

  React.useEffect(() => {
    async function loadSetting() {
      const rsetting = await config.api.setting.showSetting(
        token,
        hostname,
        settingKey
      );
      // console.log(setting)
      rsetting
        .map((setting: Setting) => setSetting(setting))
        .mapErr((err: ApiError) => setError(err));
    }
    loadSetting();
    return () => {
      setSetting(null);
      setError(null);
    };
  }, [hostname, settingKey]);

  React.useEffect(() => {
    if (settingType && setting) {
      setIsLoading(false);
    }
  }, [settingType, setting, error]);

  if (isLoading) {
    return <Loader label="Loading form..." />;
  }

  const onsubmit = async (data: any) => {
    const setting = data.formData;
    await config.api.setting.updateSetting(token, hostname, setting);
    navigate(`/admin/settings/${hostname}`, { replace: true });
  };

  return (
    <Box maxW="720px">
      <SettingBreadcrumb hostname={hostname} title={settingKey} />
      <Heading>Edit Setting</Heading>
      {/* <SettingBreadcrumb setting={setting} /> */}
      <ApiErrorUI error={error} />
      {setting && settingType && (
        <>
          <Form
            schema={settingType.schema}
            uiSchema={settingType.uiSchema}
            formData={setting}
            // onChange={() => console.log("changed")}
            onSubmit={onsubmit}
            // onError={() => console.log("errors")}
          />
          {/* <SettingDeletePopoverForm curSetting={setting} /> */}
        </>
      )}
    </Box>
  );
};
