import React from "react";
import validator from "@rjsf/validator-ajv6";
import { Box, Heading } from "@chakra-ui/react";
import { withTheme } from "@rjsf/core";
import { Theme as ChakraUITheme } from "@rjsf/chakra-ui";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../login/hooks";
import { ApiError } from "../../casualcms/domain/ports";
import { AppContext } from "../../config";
import { SettingType } from "../../casualcms/domain/model";
import { Loader } from "../layout/loader";
import { ApiErrorUI } from "../layout/error_api";
import { SettingBreadcrumb } from "../layout/breadcrumb";
// import { SettingBreadcrumb } from "../layout/breadcrumb";

const Form = withTheme(ChakraUITheme);

export const SettingNew: React.FunctionComponent<{}> = () => {
  let { hostname, settingKey } = useParams<string>();
  let auth = useAuth();
  const config = React.useContext(AppContext);
  const token = auth.authenticatedUser?.token || "";
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [settingType, setSettingType] = React.useState<SettingType | null>(
    null
  );
  const [error, setError] = React.useState<ApiError>(null);
  let navigate = useNavigate();

  React.useEffect(() => {
    async function loadType() {
      const rtyp = await config.api.settingType.showSettingType(
        token,
        settingKey || ""
      );
      rtyp
        .map((typ: SettingType) => setSettingType(typ))
        .mapErr((err: ApiError) => setError(err));
      setIsLoading(false);
    }
    if (token) {
      loadType();
    }
    return () => {
      setIsLoading(true);
      setError(null);
      setSettingType(null);
    };
  }, [auth, hostname, settingKey]);

  if (isLoading) {
    return <Loader label="Loading form..." />;
  }
  const onsubmit = async (data: any) => {
    const setting = data.formData;
    await config.api.setting.createSetting(
      token,
      hostname || "",
      settingKey || "",
      setting
    );
    navigate(`/admin/settings/${hostname}`, { replace: true });
  };

  const data = {};
  return (
    <Box maxW="720px">
      <SettingBreadcrumb hostname={hostname} title={settingKey} />
      <Heading>New Setting</Heading>
      {/* <SettingBreadcrumb title="new setting" /> */}
      <ApiErrorUI error={error} />
      {settingType && (
        <Form
          schema={settingType.schema}
          uiSchema={settingType.uiSchema}
          formData={data}
          validator={validator}
          // onChange={() => console.log("changed")}
          onSubmit={onsubmit}
          // onError={() => console.log("errors")}
        />
      )}
    </Box>
  );
};
